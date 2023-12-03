#include <iostream>
#include <cmath>
#include "windows.h"
//#include <QWidget>

/*class MainWindow : public QWidget{
    Q_OBJECT
public:
    MyWindow(QWindow *parent = nullptr) : QWindow(parent) {
        // Здесь вы можете добавить логику и отображение с использованием OpenGL или других графических библиотек
    }
};*/


double db_converter(double coeff) //конвертирует дб в разы
{
    coeff = coeff/10;
    return pow(10, coeff);
}

double once_converter(double coeff)  // конвертирует разы в дб
{
    return 10*log10(coeff);
}

double count_T_sh(double noise)   // считает риведенную ко входу шумовую температуру приемного канала
{
    return noise * 290;
}

// Считает потенциал РЛС
double count_P_rls(double p_N, double t_p, double in_coeff, double out_coeff, double l, double lose_out, double lose_in, double lose_proc, double T_sh)
{
    double P_rls = 0.0; //Потенциал РЛС
    P_rls = (p_N*t_p*in_coeff*out_coeff*pow(l, 2)*lose_out*lose_in*lose_proc)/(pow(4*M_PI,3)*1.38*pow(10, -26)*T_sh);
    return P_rls;
}

double count_OSH(double P_rls, double r, double dist, double height) // считает ОСШ
{
    double q_p_coeff = P_rls * r; // коэффициент ОСШ
    double q_p = 0.0; // ОСШ
    q_p = q_p_coeff * pow (10, -12) / pow((pow(height, 2) + pow(dist, 2)), 2);
    return q_p;
}

double count_dist_mistake(double t_p, double q_p)
{
    double C_0 = 3*pow(10, 8);
    double coeff_rectangle = sqrt(3)/(2*M_PI);
    double dist_mistake = coeff_rectangle * C_0 * t_p / sqrt(2 * q_p);
    return dist_mistake;
}



int main() {
    //Данные модели
    double v = 200;  // Скорость, м/с
    double h = 10;  // Высота, км
    double r = 50;  // Отр поверхность, м2
    double dist = 0.0; //Дистанция от начальной точки, км
    double time = 0.0;

// Данные РЛС
    double p_N = 150;  // Импульсная мощность излучаемого сигнала, кВт
    double t_p = 0.0001;  // Длительность импульса, с
    double in_coeff = 40;  // Коэффициент усиления передающей антенны, дб
    double out_coeff = 40;  // Коэффициент усиления принимающей антенны, дб
    double l = 0.035;  // Длина волны, м
    double noise = 5;  // Коэффициент шума, дб
    double lose_in = -1.5;  // Потери при приеме сигнала
    double lose_out = -1.5;  // Потери при передаче сигнала
    double lose_proc = -1;  // Потери при обработке сигнала
    double pred = pow(10, -6);  // Вероятность ложной тревоги
    double q_p = 0.0; //ОСШ
    double d_m = 0.0; // Ошибка дальности
    double P_rls = 0.0; //Потенциал РЛС
    double T_sh = 0.0; //Приведенная ко входу шумовая температура приемного канала

    std::string input;



    // Конвертируем коэффициенты из Дб в разы
    in_coeff = db_converter(in_coeff);
    out_coeff = db_converter(out_coeff);
    noise = db_converter(noise);
    lose_in = db_converter(lose_in);
    lose_out = db_converter(lose_out);
    lose_proc = db_converter(lose_proc);

    T_sh = count_T_sh(noise);
    std::cout << "Noise temperature: " << T_sh << std::endl;

    P_rls = count_P_rls(p_N, t_p, in_coeff, out_coeff, l, lose_out, lose_in, lose_proc, T_sh);
    std::cout << "radar potential: " << P_rls << std::endl;

    dist += time*v/1000;
    q_p = count_OSH(P_rls, r, dist, h);
    std::cout << "OSH: " << once_converter(q_p)<< std::endl;

    d_m = count_dist_mistake(t_p, q_p);
    std::cout << "Distant mistake: " << d_m << std::endl;


    std::cout << "Press enter to plus one second. Input smth to stop the program" << std::endl;
    while(1)
    {

        std::getline(std::cin, input);
        if (!input.empty())
            break;
        time += 1;
        dist += v/1000;
        q_p = count_OSH(P_rls, r, dist, h);
        d_m = count_dist_mistake(t_p, q_p);
        std::cout << "time: " << time << ", dist: " << dist << ", OSH in db: " << once_converter(q_p) << ", dist mistake in metres: " << d_m << std::endl;
    }

    return 0;
}
