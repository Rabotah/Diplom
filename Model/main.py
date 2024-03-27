import sys
from PyQt.window import *
import matplotlib.pyplot as plt
from functions import *

'''
#Данные модели
v = 200  # Скорость, м/с
h = 10  # Высота, км
r = 50  # Отр поверхность, м2

#Данные РЛС
p_N = 150  # Импульсная мощность излучаемого сигнала, кВт
t_p = 10**(-4)  # Длительность импульса, с
in_coeff = 40  # Коэффициент усиления передающей антенны, дб
out_coeff = 40  # Коэффициент усиления принимающей антенны, дб
l = 0.035  # Длина волны, м
noise = 5  # Коэффициент шума, дб
lose_in = -1.5  # Потери при приеме сигнала
lose_out = -1.5  # Потери при передаче сигнала
lose_proc = -1  # Потери при обработке сигнала
pred = 10**(-6)  # Вероятность ложной тревоги
DNA_width = 1 # Ширина ДНА по половинной мощности в градусах
#вектор севера откладывается от 0 по y
#(0, 0, 0) - координаты рлс

P_rls = 0.0  # Потенциал РЛС
T_sh = 0.0  # Приведенная ко входу шумовая температура приемного канала
n_iter = 1000  # количество итераций
time_step = 5  # шаг времени за 1 итерацию, с

noise = db_converter(noise)
lose_in = db_converter(lose_in)
lose_out = db_converter(lose_out)
lose_proc = db_converter(lose_proc)
in_coeff = db_converter(in_coeff)
out_coeff = db_converter(out_coeff)
DNA_width = convert_degrees_to_radians(DNA_width)
'''

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()

    P_rls = 0.0  # Потенциал РЛС
    T_sh = 0.0  # Приведенная ко входу шумовая температура приемного канала
    n_iter = 1000  # количество итераций
    time_step = 5  # шаг времени за 1 итерацию, с

    # объявление переменных, коэффициенты сразу переводим в разы
    v = window.info[0]
    h = window.info[1]
    r = window.info[2]
    p_N = window.info[3]
    t_p = window.info[4]
    in_coeff = db_converter(window.info[5])
    out_coeff = db_converter(window.info[6])
    l = window.info[7]
    noise = db_converter(window.info[8])
    lose_in = db_converter(window.info[9])
    lose_out = db_converter(window.info[10])
    lose_proc = db_converter(window.info[11])
    pred = window.info[12]
    DNA_width = convert_degrees_to_radians(window.info[13])

    T_sh = count_T_sh(noise)
    print('Шумовая температура ', T_sh)

    P_rls = count_P_rls(p_N, t_p, in_coeff, out_coeff, l,
                        lose_out, lose_in, lose_proc, T_sh)
    print('Потенциал РЛС ', P_rls)

    dist = np.zeros(n_iter)  # измерения дальности каждые 5 секунд, км
    q_p = np.zeros(n_iter)   # массив ОСШ
    d_m = np.zeros(n_iter)   # массив ошибок измерения дальности, км
    p_m = np.zeros(n_iter)   # массив ошибок определения углового положения
    azimuth = np.zeros(n_iter)  # массив азимутов, рад
    seat_angle = np.zeros(n_iter)  # массив углов места, рад
    sigma_x = np.zeros(n_iter)  # массив ошибок преобразования x координаты
    sigma_y = np.zeros(n_iter)  # массив ошибок преобразования y координаты
    sigma_z = np.zeros(n_iter)  # массив ошибок преобразования z координаты

    # Значения ошибок при R = 0
    q_p[0] = count_OSH(P_rls, r, 0, h)
    d_m[0] = count_dist_mistake(t_p, q_p[0])
    p_m[0] = count_ang_pos_mistake(DNA_width, q_p[0])
    seat_angle[0] = 0
    azimuth[0] = convert_degrees_to_radians(80)
    sigma_x[0] = count_sigma_x(0, seat_angle[0], azimuth[0], d_m[0], p_m[0])
    sigma_y[0] = count_sigma_y(0, seat_angle[0], azimuth[0], d_m[0], p_m[0])
    sigma_z[0] = count_sigma_z(0, seat_angle[0], azimuth[0], d_m[0], p_m[0])

    # считаем значения дальности и ошибок каждые 5с 1000 раз
    for t in range(1, n_iter):
        dist[t] = dist[t-1] + v*time_step*10**(-3)
        q_p[t] = count_OSH(P_rls, r, dist[t], h)
        d_m[t] = count_dist_mistake(t_p, q_p[t])
        p_m[t] = count_ang_pos_mistake(DNA_width, q_p[t])
        seat_angle[t] = count_seat_angle(dist[t], h)
        azimuth[t] = azimuth[t-1] + convert_degrees_to_radians(0.0005)
        sigma_x[t] = count_sigma_x(dist[t], seat_angle[t], azimuth[t], d_m[t], p_m[t])
        sigma_y[t] = count_sigma_y(dist[t], seat_angle[t], azimuth[t], d_m[t], p_m[t])
        sigma_z[t] = count_sigma_z(dist[t], seat_angle[t], azimuth[t], d_m[t], p_m[t])

    # зашумляем значения дальности ошибка дальности*5
    # чтобы данные хоть немного отличимы были
    dist += np.random.normal(0, d_m*4)

    #МНК
    time = np.arange(0, n_iter*time_step, 5)
    time_x = np.vstack([time, np.ones(len(time))]).T
    a, c = np.linalg.lstsq(time_x, dist, rcond=None)[0]

    # считаем количество отклонений из доверительного интервала
    mistakes = dist - a*time - c
    pers_m = mistakes > d_m*3
    result = np.sum(pers_m)/n_iter*100
    print('% отклонений от доверительного интервала: ', result)


    fig, ax =  plt.subplots(2, 2, figsize=(10,10))

    #рисуем траекторию + при помощи мнк простраиваем предполагаемую истинную
    ax[0, 0].scatter(time, dist, s = 3)
    ax[0, 0].plot(time, a*time + c, color = 'r')
    ax[0, 0].set_title('% отклонений: ' + str(round(result, 2)))
    ax[0, 0].legend(['измерения дальности, км', 'траектория'])
    ax[0, 0].set_xlabel('Время, с')
    ax[0, 0].set_ylabel('Дальность, км')

    # ошибки определения  координат
    ax[0, 1].plot(time, sigma_x, color = 'r', linewidth=3)
    ax[0, 1].plot(time, sigma_y, color = 'b')
    ax[0, 1].plot(time, sigma_z, color = 'g')
    ax[0, 1].legend(['x', 'y', 'z'])
    ax[0, 1].set_xlabel('Время, с')
    ax[0, 1].set_ylabel('Ошибка определения координат, км')

    # зависимость ошибки дальности от времени
    ax[1, 0].plot(time, d_m*10**(-3), color = 'g')
    ax[1, 0].set_xlabel('Время, с')
    ax[1, 0].set_ylabel('Ошибка дальности, км')

    # зависимость ошибки определения углового положения от времени
    ax[1, 1].plot(time, p_m, color = 'm')
    ax[1, 1].set_xlabel('Время, с')
    ax[1, 1].set_ylabel('Ошибка углового положения, °')

    fig.tight_layout(h_pad= 4)
    plt.show()










