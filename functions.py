import numpy as np

#конвертирует дб в разы
def db_converter(coeff):
    return 10**(coeff/10)

#конвертирует разы в дб
def once_converter(coeff):
    return 10*np.log10(coeff)

#считает риведенную ко входу шумовую температуру приемного канала
def count_T_sh(noise):
    return noise*290

#Считает потенциал РЛС
def count_P_rls(p_N, t_p, in_coeff, out_coeff, l, lose_out, lose_in, lose_proc, T_sh):
    P_rls = 0.0
    P_rls = (p_N * t_p * in_coeff * out_coeff * l**2 * lose_out * lose_in * lose_proc) / (
            (4 * np.pi)**3 * 1.38 * 10**(-26) * T_sh)
    return P_rls

#Считает ОСШ
def count_OSH (P_rls, r, dist, height):
    q_p = 0.0
    q_p = P_rls * r * 10**(-12) / (height**2 + dist**2)**2
    return q_p

#Считаем ошибку измерения дистанции
def count_dist_mistake(t_p, q_p):
    dist_mistake = 0.0
    C_0 = 3 * 10**5
    P_eff = np.pi / (t_p * np.sqrt(3))  # Эффективная ширина спектра сигнала для прямоугольного импульса
    dist_mistake = C_0 /(2 * np.sqrt(2 * q_p) * P_eff)
    return dist_mistake

#Считаем ошибку определения углового положения
def count_ang_pos_mistake(DNA_width, q_p):
    pos_mistake = 0.0
    K_prop = 1 / np.sqrt(np.pi) #Коэффициент пропорциональности для прямоугольного импульса
    pos_mistake = K_prop * DNA_width / np.sqrt(2 * q_p)
    return pos_mistake

def convert_degrees_to_radians(degrees):
    return degrees*np.pi/180

# считаем угол места (принимаем за истину то, что высота не меняется)
def count_seat_angle(dist, h):
    return convert_degrees_to_radians(np.arcsin(h/dist))

def count_sigma_x(dist, angle, azimuth, sigma_dist, sigma_angle):
    first = (np.cos(angle)*np.cos(azimuth)*sigma_dist)**2
    second = (dist*np.cos(angle)*np.sin(azimuth)*sigma_angle)**2
    third = (dist*np.sin(angle)*np.cos(azimuth)*sigma_angle)**2
    return np.sqrt(first + second + third)

def count_sigma_y(dist, angle, azimuth, sigma_dist, sigma_angle):
    first = (np.cos(angle) * np.sin(azimuth) * sigma_dist) ** 2
    second = (dist * np.cos(angle) * np.cos(azimuth) * sigma_angle) ** 2
    third = (dist * np.sin(angle) * np.sin(azimuth) * sigma_angle) ** 2
    return np.sqrt(first + second + third)

def count_sigma_z(dist, angle, azimuth, sigma_dist, sigma_angle):
    first = (np.sin(angle) * sigma_dist) ** 2
    second = 0
    third = (dist * np.cos(angle) * sigma_angle) ** 2
    return np.sqrt(first + second + third)

