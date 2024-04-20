from PyQt.window import *
import matplotlib.pyplot as plt
from functions import *
from sys import argv
from PyQt6.QtWidgets import QApplication
from numpy import zeros, arange, vstack, linalg, ones
from numpy.random import normal

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
first_dist = 0
first_azimuth = 70
coeff = 3
#вектор севера откладывается от 0 по y
#(0, 0, 0) - координаты рлс

P_rls = 0.0  # Потенциал РЛС
T_sh = 0.0  # Приведенная ко входу шумовая температура приемного канала
n_iter = 1000  # количество итераций
time_step = 10  # шаг времени за 1 итерацию, с
mnk_step = 10

noise = db_converter(noise)
lose_in = db_converter(lose_in)
lose_out = db_converter(lose_out)
lose_proc = db_converter(lose_proc)
in_coeff = db_converter(in_coeff)
out_coeff = db_converter(out_coeff)
DNA_width = convert_degrees_to_radians(DNA_width)
'''

if __name__ == "__main__":
    app = QApplication(argv)
    window = MyWindow()
    window.show()
    app.exec()

    P_rls = 0.0  # Потенциал РЛС
    T_sh = 0.0  # Приведенная ко входу шумовая температура приемного канала
    n_iter = 1000  # количество итераций
    time_step = 5  # шаг времени за 1 итерацию, с
    coeff = 3
    mnk_step = 10

    print('\n', '-'*30, 'Начало расчётов', '-'*30)

    # объявление переменных, коэффициенты сразу переводим в разы
    v = window.info[0]
    h = window.info[1]
    r = window.info[2]
    p_N = window.info[3]
    t_p = window.info[4]
    if (t_p == 0):
        print('Введена нулевая длительность импульса')
        user_input = input("Нажмите enter, чтобы выйти")
        exit(-1)
    in_coeff = db_converter(window.info[5])
    out_coeff = db_converter(window.info[6])
    l = window.info[7]
    noise = db_converter(window.info[8])
    lose_in = db_converter(window.info[9])
    lose_out = db_converter(window.info[10])
    lose_proc = db_converter(window.info[11])
    pred = window.info[12]
    DNA_width = convert_degrees_to_radians(window.info[13])
    first_azimuth = window.info[15]
    first_dist = window.info[14]

    T_sh = count_T_sh(noise)
    print('Шумовая температура ', T_sh)

    try:
        P_rls = count_P_rls(p_N, t_p, in_coeff, out_coeff, l,
                            lose_out, lose_in, lose_proc, T_sh)
    except ZeroDivisionError:
        print('Ошибка деления на 0')
        user_input = input("Нажмите enter, чтобы выйти")
        exit(-1)

    print('Потенциал РЛС ', P_rls)

    way = zeros(n_iter)  # пройденный путь, км
    dist = zeros(n_iter)  # измерения дальности каждые 5 секунд, км
    q_p = zeros(n_iter)   # массив ОСШ
    d_m = zeros(n_iter)   # массив ошибок измерения дальности, км
    p_m = zeros(n_iter)   # массив ошибок определения углового положения
    azimuth = zeros(n_iter)  # массив азимутов, рад
    seat_angle = zeros(n_iter)  # массив углов места, рад
    sigma_x = zeros(n_iter)  # массив ошибок преобразования x координаты
    sigma_y = zeros(n_iter)  # массив ошибок преобразования y координаты
    sigma_z = zeros(n_iter)  # массив ошибок преобразования z координаты
    trajectory = zeros(n_iter)  # массив ошибок преобразования z координаты

    # Значения ошибок при R = 0
    way[0] = first_dist
    dist[0] = sqrt(h**2 + way[0]**2)
    q_p[0] = count_OSH(P_rls, r, dist[0], h)
    d_m[0] = count_dist_mistake(t_p, q_p[0])
    p_m[0] = count_ang_pos_mistake(DNA_width, q_p[0])
    seat_angle[0] = count_seat_angle(dist[0], h)
    azimuth[0] = convert_degrees_to_radians(first_azimuth)
    sigma_x[0] = count_sigma_x(0, seat_angle[0], azimuth[0], d_m[0], p_m[0])
    sigma_y[0] = count_sigma_y(0, seat_angle[0], azimuth[0], d_m[0], p_m[0])
    sigma_z[0] = count_sigma_z(0, seat_angle[0], azimuth[0], d_m[0], p_m[0])

    # считаем значения дальности и ошибок каждые 5с 1000 раз
    for t in range(1, n_iter):
        way[t] = way[t-1] + v*time_step*10**(-3)
        dist[t] = sqrt(h**2 + way[t]**2)
        q_p[t] = count_OSH(P_rls, r, dist[t], h)
        d_m[t] = count_dist_mistake(t_p, q_p[t])
        p_m[t] = count_ang_pos_mistake(DNA_width, q_p[t])
        seat_angle[t] = count_seat_angle(dist[t], h)
        azimuth[t] = azimuth[t-1] + convert_degrees_to_radians(0.0005)
        sigma_x[t] = count_sigma_x(dist[t], seat_angle[t], azimuth[t], d_m[t], p_m[t])
        sigma_y[t] = count_sigma_y(dist[t], seat_angle[t], azimuth[t], d_m[t], p_m[t])
        sigma_z[t] = count_sigma_z(dist[t], seat_angle[t], azimuth[t], d_m[t], p_m[t])
        # МНК
        if ((t+1) % mnk_step == 0):
            time = arange((t-mnk_step+1)*time_step, (t+1) * time_step, time_step)
            time_x = vstack([time, ones(mnk_step)]).T
            a, c = linalg.lstsq(time_x, dist[t-mnk_step+1:t+1], rcond=None)[0]
            trajectory[t-mnk_step+1:t+1] = a*time + c



    # зашумляем значения дальности ошибка дальности*5
    # чтобы данные хоть немного отличимы были
    dist += normal(0, d_m)
    time = arange(0.01, n_iter*time_step, time_step)

    # считаем количество отклонений из доверительного интервала
    mistakes = dist - trajectory
    mist_ind = (mistakes > d_m*coeff) | (mistakes < -d_m*coeff)
    right_ind = (mistakes <= d_m*coeff) & (mistakes >= -d_m*coeff)
    mistakes_points = dist[mist_ind]
    right_points = dist[right_ind]
    result = sum(mist_ind)/n_iter*100
    print('% отклонений от доверительного интервала: ', result)


    #рисуем траекторию + при помощи мнк простраиваем предполагаемую истинную
    plt.figure(figsize=(20,20))
    plt.scatter(time[mist_ind], mistakes_points, color = 'r', s = 1)
    plt.scatter(time[right_ind], right_points, color='b', s=1)
    plt.plot(time, trajectory, color = 'm')
    plt.plot(time, a*time + c + d_m*coeff, color='g')
    plt.plot(time, a*time + c - d_m*coeff, color='g')
    #plt.sub('% отклонений: ' + str(round(result, 2)))
    plt.legend(['выбросы', 'измерения дальности, км', 'траектория', 'доверительный интервал'])
    plt.xlabel('Время, с')
    plt.ylabel('Дальность, км')
    plt.show()

    '''
    p_m = convert_radians_to_degrees(p_m)
    seat_angle = convert_radians_to_degrees(seat_angle)
    seat_angle += normal(0, p_m)
    line = fit_curve(time, seat_angle)
    
    # считаем количество отклонений из доверительного интервала
    
    mistakes = seat_angle - line
    mist_ind = (mistakes > p_m*coeff) | (mistakes < -p_m*coeff)
    right_ind = (mistakes <= p_m*coeff) & (mistakes >= -p_m*coeff)
    mistakes_points = seat_angle[mist_ind]
    right_points = seat_angle[right_ind]
    result = sum(mist_ind)/n_iter*100
    print('% отклонений от доверительного интервала: ', result)
    
    
    #рисуем траекторию + при помощи мнк простраиваем предполагаемую истинную
    plt.figure(figsize=(20,20))
    plt.scatter(time[mist_ind], mistakes_points, color = 'r', s = 1)
    plt.scatter(time[right_ind], right_points, color='b', s=1)
    plt.plot(time, line, color = 'm')
    plt.plot(time, line + p_m*coeff, color='g')
    plt.plot(time, line - p_m*coeff, color='g')
    #plt.sub('% отклонений: ' + str(round(result, 2)))
    plt.legend(['выбросы', 'измерения угла места, °', 'истинное изменение', 'доверительный интервал'])
    plt.xlabel('Время, с')
    plt.ylabel('Угол места, °')
    plt.show()
    '''
    fig, ax =  plt.subplots(3, 1, figsize=(10,10))

    # ошибки определения  координат
    ax[0].plot(time, sigma_x, color = 'r')
    ax[0].plot(time, sigma_y, color = 'b')
    ax[0].plot(time, sigma_z, color = 'g')
    ax[0].legend(['x', 'y', 'z'])
    ax[0].set_xlabel('Время, с')
    ax[0].set_ylabel('Ошибка определения координат, км')

    # зависимость ошибки дальности от времени
    ax[1].plot(time, d_m*10**(-3), color = 'g')
    ax[1].set_xlabel('Время, с')
    ax[1].set_ylabel('Ошибка дальности, км')

    # зависимость ошибки определения углового положения от времени
    ax[2].plot(time, p_m, color = 'm')
    ax[2].set_xlabel('Время, с')
    ax[2].set_ylabel('Ошибка углового положения, °')

    fig.tight_layout(h_pad= 4)
    plt.show()










