from sys import argv
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, \
    QPushButton, QLabel, QLineEdit, QFileDialog, QMessageBox
from functions import is_float
from PyQt6.QtCore import Qt

number_of_parametrs = 16
class ManualInputWindow(QWidget):
    def __init__(self, info: list, labels: list):

        self.info = info
        self.labels = labels
        self.texts = []

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

        label = QLabel("<b><font size=4>Введите данные цели и РЛС</font></b>")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        input_layout3.addWidget(label)

        # Создание ячеек ввода в 2 ряда
        for i in range (number_of_parametrs//2):
            label = QLabel("Введите " + self.labels[i])
            input_layout1.addWidget(label)
            lineEdit = QLineEdit()
            input_layout1.addWidget(lineEdit)
            self.texts.append(lineEdit)

        for i in range (number_of_parametrs//2, len(self.info)):
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

class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.labels = ["скорость модели, м/с", "высоту модели, км", "отражающую поверхность модели, м^2",
        "импульсную мощность излучаемого сигнала, кВт", "длительность импульса, с",
        "коэффициент усиления передающей антенны, дб", "коэффициент усиления принимающей антенны, дб",
        "длину волны, м", "коэффициент шума, дб", "потери при приеме сигнала, дб",
        "потери при передаче сигнала, дб","потери при обработке сигнала, дб", "вероятность ложной тревоги",
                       "ширину ДНА по половинной мощности, °", "начальную дальность до РЛС, км", "начальный азимут, °"]
        self.info = [0.0]*number_of_parametrs
        self.is_okay = False

        self.is_loaded = False

        self.setWindowTitle("Выберите тип ввода")
        self.manual_input_window = ManualInputWindow(self.info, self.labels)

        self.manual_input_button = QPushButton("Ручной ввод", self)
        self.manual_input_button.clicked.connect(self.show_manual_input)

        self.load_button = QPushButton("Загрузить файл", self)
        self.load_button.clicked.connect(self.load_file)

        layout = QVBoxLayout()
        layout.addWidget(self.manual_input_button)
        layout.addWidget(self.load_button)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)


    def show_manual_input(self):
        self.manual_input_window.show()

    def load_file(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Выберите файл", "", "Text Files (*.txt)")

        if filename:
            try:
                with open(filename, 'r') as file:
                    lines = file.readlines()
                    if len(lines) >= number_of_parametrs:
                        self.is_okay = True
                        for i, line in enumerate(lines):
                            text = str(line).replace(',', '.')
                            if is_float(text):
                                self.info[i] = float(text)
                                print(f"Ввели {self.labels[i]}: {self.info[i]}")
                            else:
                                print(
                                    f"Ошибка: Вы неверно ввели {self.labels[i]}. Введите только целые или вещественные числа")
                                self.is_okay = False
                        if (self.is_okay):
                            self.close()
            except Exception:
                QMessageBox.warning(self, "Error", "Ошибка чтения файла")


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
                exit(0)
            else:
                event.ignore()

