from numpy import log10, pi, sqrt, cos, sin, arcsin
from scipy.optimize import curve_fit

def is_float(text):
    try:
        float(text)
        return True
    except ValueError:
        return False

#конвертирует дб в разы
def db_converter(coeff):
    return 10**(coeff/10)

#конвертирует разы в дб
def once_converter(coeff):
    return 10*log10(coeff)

#считает риведенную ко входу шумовую температуру приемного канала
def count_T_sh(noise):
    return noise*290

#Считает потенциал РЛС
def count_P_rls(p_N, t_p, in_coeff, out_coeff, l, lose_out, lose_in, lose_proc, T_sh):
    P_rls = 0.0
    P_rls = (p_N * t_p * in_coeff * out_coeff * l**2 * lose_out * lose_in * lose_proc) / (
            (4 * pi)**3 * 1.38 * 10**(-26) * T_sh)
    return P_rls

#Считает ОСШ
def count_OSH (P_rls, r, dist, height):
    try:
        q_p = P_rls * r * 10**(-12) / (height**2 + dist**2)**2
    except ZeroDivisionError:
        q_p = 0.0
    return q_p

#Считаем ошибку измерения дистанции
def count_dist_mistake(t_p, q_p):
    C_0 = 3 * 10**5
    P_eff = pi / (t_p * sqrt(3))  # Эффективная ширина спектра сигнала для прямоугольного импульса
    dist_mistake = C_0 / (2 * sqrt(2 * q_p) * P_eff)
    return dist_mistake

#Считаем ошибку определения углового положения
def count_ang_pos_mistake(DNA_width, q_p):
    K_prop = 1 / sqrt(pi) #Коэффициент пропорциональности для прямоугольного импульса
    try:
        pos_mistake = K_prop * DNA_width / sqrt(2 * q_p)
    except ZeroDivisionError:
        pos_mistake = 0.0
    return pos_mistake

def convert_degrees_to_radians(degrees):
    return degrees*pi/180

def convert_radians_to_degrees(radians):
    return radians*180/pi

# считаем угол места (принимаем за истину то, что высота не меняется)
def count_seat_angle(dist, h):
    if h == 0 or dist == 0:
        return 0
    else:
        return arcsin(h/dist)

def count_sigma_x(dist, angle, azimuth, sigma_dist, sigma_angle):
    first = (cos(angle)*cos(azimuth)*sigma_dist)**2
    second = (dist*cos(angle)*sin(azimuth)*sigma_angle)**2
    third = (dist*sin(angle)*cos(azimuth)*sigma_angle)**2
    return sqrt(first + second + third)

def count_sigma_y(dist, angle, azimuth, sigma_dist, sigma_angle):
    first = (cos(angle) * sin(azimuth) * sigma_dist) ** 2
    second = (dist * cos(angle) * cos(azimuth) * sigma_angle) ** 2
    third = (dist * sin(angle) * sin(azimuth) * sigma_angle) ** 2
    return sqrt(first + second + third)

def count_sigma_z(dist, angle, azimuth, sigma_dist, sigma_angle):
    first = (sin(angle) * sigma_dist) ** 2
    second = 0
    third = (dist * cos(angle) * sigma_angle) ** 2
    return sqrt(first + second + third)

def quadratic_func(x, a, b, c, d, e):
    return a * x**(-4) + b * x**(-3) + c * x**(-2) + d* x**(-1) + e

def fit_curve(x, y):
    popt, pcov = curve_fit(quadratic_func, x, y, maxfev=200000)
    print(*popt)
    return quadratic_func(x, *popt)