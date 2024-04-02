from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QMessageBox, \
    QWidget, QLabel, QLineEdit, QPushButton, QHBoxLayout, QGridLayout
from PyQt6.QtCore import Qt, QCoreApplication
import sys

# проверка вводных данных
def is_float(text):
    try:
        float(text)
        return True
    except ValueError:
        return False

class MainWindow(QWidget):
    def __init__(self):

        self.labels = ["скорость модели, м/с", "высоту модели, км", "отражающую поверхность модели, м^2",
        "импульсную мощность излучаемого сигнала, кВт", "длительность импульса, с",
        "коэффициент усиления передающей антенны, дб", "коэффициент усиления принимающей антенны, дб",
        "длину волны, м", "коэффициент шума, дб", "потери при приеме сигнала, дб",
        "потери при передаче сигнала, дб","потери при обработке сигнала, дб", "вероятность ложной тревоги",
                       "ширину ДНА по половинной мощности, °", "начальную дальность до РЛС, км", "начальный азимут, °"]
        self.info = [0.0]*16
        self.texts = []
        self.is_okay = False

        # запускаем функции
        super().__init__()
        self.new_window()

    # функция создания нового окна
    def new_window(self):
        main_layout = QHBoxLayout()
        layout = QVBoxLayout()
        input_layout1 = QVBoxLayout()
        input_layout2 = QVBoxLayout()
        input_layout3 = QVBoxLayout()

        label = QLabel("<b><font size=4>Введя данные нажмите кнопку Enter</font></b>")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        input_layout3.addWidget(label)

        # Создание ячеек ввода в 2 ряда
        for i in range (len(self.info)//2):
            label = QLabel("Введите " + self.labels[i])
            input_layout1.addWidget(label)
            lineEdit = QLineEdit()
            input_layout1.addWidget(lineEdit)
            self.texts.append(lineEdit)

        for i in range (len(self.info)//2, len(self.info)):
            label = QLabel("Введите " + self.labels[i])
            input_layout2.addWidget(label)
            lineEdit = QLineEdit()
            input_layout2.addWidget(lineEdit)
            self.texts.append(lineEdit)

        # размещение слоёв интерфейса
        layout.addLayout(input_layout3)
        main_layout.addLayout(input_layout1)
        main_layout.addLayout(input_layout2)
        layout.addLayout(main_layout)

        # кнопка запуска программы, проверяющая и сохранябющая введенные данные
        save_button = QPushButton("Запустить программу")
        save_button.clicked.connect(self.validateAndAssign)
        layout.addWidget(save_button)
        self.setLayout(layout)

    # функция проверки введённых данных
    def validateAndAssign(self):
        self.is_okay = True
        for i, line_edit in enumerate(self.texts):
            text = line_edit.text().replace(',', '.')
            if is_float(text):
                self.info[i] = float(text)
                print(f"Ввели {self.labels[i]}: {self.info[i]}")
            else:
                print(f"Ошибка: Вы неверно ввели {self.labels[i]}. Введите только целые или вещественные числа")
                self.is_okay = False
        if (self.is_okay):
            self.close()

    # логика закрытия окна ввода данных
    def closeEvent(self, event):
        # окно подтверждения
        if (self.is_okay):
            event.accept()
        else:
            reply = QMessageBox.question(self, "Подтверждение",
                                         "Вы действительно хотите остановить программу?",
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

            # при подтверждении основное окно закрывается, программа завершается
            # иначе закрывается окно подтверждения
            if reply == QMessageBox.StandardButton.Yes:
                event.accept()
                sys.exit(0)
            else:
                event.ignore()
