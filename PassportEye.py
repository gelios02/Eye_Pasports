import glob
import json
import os
import pytesseract
import sys
import numpy as np
import math
import re
import time
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QFileDialog
from PasportEye_design import Ui_MainWindow
from PyQt5.QtCore import QBasicTimer
from cv2 import cv2


pytesseract.pytesseract.tesseract_cmd = r"Tesseract-OCR\tesseract.exe" #подклачаем Tessract


class PassportEye(QtWidgets.QMainWindow): # создаем класс и передаем в него наш собранный дизайн
    def __init__(self):
        super(PassportEye, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.init_UI()
        self.setWindowTitle("PassportEye")
        self.setWindowIcon(QtGui.QIcon("Resourse/logo_app.png"))
    def init_UI(self):
        self.ui.choose_pass.clicked.connect(self.file_path) # кнопка для получения фото
        self.ui.process.clicked.connect(self.process)# кнопка для обработки данных с фото
        self.ui.choose_json.clicked.connect(self.directore_open)# кнопка для открытия директории JSON,который будет использоваться для парсинга






    def process(self): # функция обработки фотографии
        self.completed = 0
        while self.completed < 100:
            self.completed += 0.00001
            self.ui.progressBar.setValue(self.completed)  #загрузка для sroll bar

        with open('Processing/process.txt', 'r', encoding='utf-8') as t: # создаем файл обработки
            content = t.read()
        img = cv2.imread(content)
        img_copy = img.copy()  # далее с помощью линийи Хоффа определяем нужный нам объкт и вырезаем его с фона
        img_canny = cv2.Canny(img_copy, 50, 100, apertureSize=3)
        img_hough = cv2.HoughLinesP(img_canny, 1, math.pi / 180, 100, minLineLength=50, maxLineGap=10)
        (x, y, w, h) = (np.amin(img_hough, axis=0)[0, 0], np.amin(img_hough, axis=0)[0, 1],
                        np.amax(img_hough, axis=0)[0, 0] - np.amin(img_hough, axis=0)[0, 0],
                        np.amax(img_hough, axis=0)[0, 1] - np.amin(img_hough, axis=0)[0, 1])
        img_roi = img_copy[y:y + h, x:x + w]
        res_img = cv2.resize(img_roi, (1152, 1630), cv2.INTER_NEAREST) # приводим плученное изображение к единому разрешению

        # cv2.imshow('img', res_img)
        img0 = res_img[112:340, 200:1080]  # получаем шаблоны для считывания данных с паспорта
        cv2.imwrite('Temp\\img0.jpg', img0)
        img1 = res_img[309:419, 190:500]
        cv2.imwrite("Temp\\img1.jpg", img1)
        img2 = res_img[313:400, 600:1080]
        cv2.imwrite("Temp\\img2.jpg", img2)
        img3 = res_img[185:700, 1000:1200]
        cv2.imwrite("Temp\\img3.jpg", img3)
        img4 = res_img[890:1180, 480:1010]
        cv2.imwrite("Temp\\img4.jpg", img4)
        img5 = res_img[1140:1242, 649:1051]
        cv2.imwrite("Temp\\img5.jpg", img5)
        img6 = res_img[1205:1390, 450:1050]
        cv2.imwrite("Temp\\img6.jpg", img6)
        img7 = res_img[1148:1238, 395:571]
        cv2.imwrite("Temp\\img7.jpg", img7)

        pictures = sorted(os.listdir('Temp/')) # ортируем полученные фотографии в директорию Temp для последующей обработки
        # Упорядочим список

        for i, picture in enumerate(pictures):
            # считываем изображение в picture
            # print(picture)
            picture = cv2.imread('Temp/' + picture)
            # image = cv2.imread("Temp/")
            gray = cv2.cvtColor(picture, cv2.COLOR_BGR2GRAY) # далее обработка по Гауса
            blur = cv2.GaussianBlur(gray, (3, 3), 0)
            thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

            # Morph для удаления шума и инвертирования изображения
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
            opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=1)
            invert = 255 - opening
            filename = "ocr{}.jpg"
            filename = filename.format(i)
            cv2.imwrite(f'Processing\\{filename}', invert)

            # print(i)
        pas_issue = pytesseract.image_to_string('Processing/ocr0.jpg', lang='rus', config='--psm 11--oem 1') # бработанную фотографию отсылаем Tessercat, и указываем особые парметры для считываняи в зависимости от типа дынных в данном конкретном шаблоне
        # print('Паспорт выдан: \n ',lastname_chi)
        with open('Processing/text.txt', 'w', encoding='utf-8') as f:
            f.write(pas_issue)
        with open('Processing/text.txt', "r", encoding='utf-8') as f:
            content = f.read()
            c = re.sub("[,@#$%^&*()""“_+/=:;?!']", " ", # исключаем символы
                       content)
        with open('Processing/text.txt', 'w', encoding='utf-8') as f:
            f.write(c)
        with open('Processing/text.txt', 'r', encoding='utf-8') as t:
            content = t.readlines()
        content = [x.strip() for x in content]
        new_content = []
        for i in content:
            if len(str(i)) > 10: # если длина строки больше 10 то добовляем в файл
                new_content.append(i)
                # print(content)
        read_1 = new_content
        # display_1 = print('Паспорт выдан:', new_content)

        date_issue = pytesseract.image_to_string('Processing/ocr1.jpg', lang='rus', # здесь происходить тоже передача фото Tesseract с парматерами
                                                 config='--psm 3--oem 1 -c tessedit_char_whitelist=.0123456789')
        with open('Processing/text0.txt', 'w', encoding='utf-8') as f:
            f.write(date_issue)
        with open('Processing/text0.txt', "r", encoding='utf-8') as f:
            content = f.read()
            c = re.sub("[ёйцукенгшщзхъфывапролджэячсмитьбюЁЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭЯЧСМИТЬБЮ,@#$%^&*()_+/=:;?!' ]", " ",# исключаем символы
                       content)
        with open('Processing/text0.txt', 'w', encoding='utf-8') as f:
            f.write(c)
        with open('Processing/text0.txt', 'r', encoding='utf-8') as t:
            content = t.readlines()
        content = [x.strip() for x in content]
        new_content = []
        for i in content:
            if len(str(i)) > 4: # если длина строки больше 4 то добовляем в файл
                new_content.append(i)
        read_2 = new_content
        # display_2 = print('Дата выдачи:', new_content)

        division_code = pytesseract.image_to_string('Processing/ocr2.jpg', lang='rus',
                                                    config='--psm 3--oem 1 -c tessedit_char_whitelist=-0123456789')
        with open('Processing/text1.txt', 'w', encoding='utf-8') as f:
            f.write(division_code)
        with open('Processing/text1.txt', "r", encoding='utf-8') as f:
            content = f.read()
            c = re.sub("[ёйцукенгшщзхъфывапролджэячсмитьбюЁЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭЯЧСМИТЬБЮ,@#$%^&*()_+/=:;?!' ]", " ",# исключаем символы
                       content)
        with open('Processing/text1.txt', 'w', encoding='utf-8') as f:
            f.write(c)
        with open('Processing/text1.txt', 'r', encoding='utf-8') as t:
            content = t.readlines()
        content = [x.strip() for x in content]
        new_content = []
        for i in content:
            if len(str(i)) > 4:
                new_content.append(i)
        read_3 = new_content
        # display_3 = print('Код подразделения:', new_content)

        num_pasp = pytesseract.image_to_string('Processing/ocr3.jpg', lang='rus',
                                               config='--psm 5--oem 1 -c tessedit_char_whitelist=0123456789')
        with open('Processing/text2.txt', 'w', encoding='utf-8') as f:
            f.write(num_pasp)
        with open('Processing/text2.txt', "r", encoding='utf-8') as f:
            content = f.read()
            c = re.sub("[ёйцукенгшщзхъфывапролджэячсмитьбюЁЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭЯЧСМИТЬБЮ,@#$%^&*()_+/=:;?!' ]", " ",
                       content)
        with open('Processing/text2.txt', 'w', encoding='utf-8') as f:
            f.write(c)
        with open('Processing/text2.txt', 'r', encoding='utf-8') as t:
            content = t.readlines()
        content = [x.strip() for x in content]
        new_content = []
        for i in content:
            if len(str(i)) > 4:
                new_content.append(i)
        read_4 = new_content
        # display_4 = print('Номер паспорта:', new_content)

        fio = pytesseract.image_to_string('Processing/ocr4.jpg', lang='rus', config='--psm 6--oem 3')
        with open('Processing/text3.txt', 'w', encoding='utf-8') as f:
            f.write(fio)
        with open('Processing/text3.txt', "r", encoding='utf-8') as f:
            content = f.read()
            c = re.sub("[0-9,@#$%^&*©()_}{<>|.+/=:;?!' ]", "",
                       content)
        with open('Processing/text3.txt', 'w', encoding='utf-8') as f:
            f.write(c)
        with open('Processing/text3.txt', 'r', encoding='utf-8') as t:
            content = t.readlines()

        content = [x.strip() for x in content]
        new_content = []
        for i in content:
            if len(str(i)) >= 5:
                new_content.append(i)
                # print(content)
        read_5 = new_content

        date_birth = pytesseract.image_to_string('Processing/ocr5.jpg', lang='rus',
                                                 config='--psm 3 --oem 1 -c tessedit_char_whitelist=.0123456789')
        with open('Processing/text4.txt', 'w', encoding='utf-8') as f:
            f.write(date_birth)
        with open('Processing/text4.txt', "r", encoding='utf-8') as f:
            content = f.read()
            c = re.sub("[ёйцукенгшщзхъфывапролджэячсмитьбюЁЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭЯЧСМИТЬБЮ,@#$%^&*()_+/|=:;?!' ]", " ",
                       content)
        with open('Processing/text4.txt', 'w', encoding='utf-8') as f:
            f.write(c)
        with open('Processing/text4.txt', 'r', encoding='utf-8') as t:
            content = t.readlines()

        content = [x.strip() for x in content]
        new_content = []
        for i in content:
            if len(str(i)) >= 5:
                new_content.append(i)
                # print(content)
        read_6 = new_content
        # display_6 = print('Дата рождения:', new_content)

        place_birth = pytesseract.image_to_string('Processing/ocr6.jpg', lang='rus', config='--psm 6--oem 3')
        with open('Processing/text5.txt', 'w', encoding='utf-8') as f:
            f.write(place_birth)
        with open('Processing/text5.txt', "r", encoding='utf-8') as f:
            content = f.read()
            c = re.sub("[0-9,йцукенгшщзхъфывапролджэячсмитьбюё@#$%^&*()_+/=:;?!']", "", content)
        with open('Processing/text5.txt', 'w', encoding='utf-8') as f:
            f.write(c)
        with open('Processing/text5.txt', 'r', encoding='utf-8') as t:
            content = t.readlines()

        content = [x.strip() for x in content]
        new_content = []
        for i in content:

            if len(str(i)) >= 4:
                new_content.append(i)
                # print(content)
        read_7 = new_content
        # display_7 = print('Место рождения:', new_content)

        sex = pytesseract.image_to_string('Processing/ocr7.jpg', lang='rus', config='--psm 6--oem 1')
        with open('Processing/text6.txt', 'w', encoding='utf-8') as f:
            f.write(sex)
        with open('Processing/text6.txt', "r", encoding='utf-8') as f:
            content = f.read()
            c = re.sub("[0-9,УЕНцукенгшщзхъфывапролджэячсмитьбюЙЦКГШЩЗХФЫВАПРОЛДЯЧСИТЬБЮ@#$%^&*()_|+<>/=:;?!']", "",
                       content)
        with open('Processing/text6.txt', 'w', encoding='utf-8') as f:
            f.write(c)
        with open('Processing/text6.txt', 'r', encoding='utf-8') as t:
            content = t.readlines()

        content = [x.strip() for x in content]
        new_content = []
        for i in content:

            if len(str(i)) >= 2:
                new_content.append(i)
                # print(content)
        read_8 = new_content
        # display_8 = print('Пол:', new_content)

        data_display = {}  # создаем русский шаблон для вывода данных в Label в приложении
        data_display['PasportEye'] = []
        data_display['PasportEye'].append({
            'Паспорт выдан': read_1,
            'Дата выдачи': read_2,
            'Код поддразделения': read_3,
            'Номер паспорта': read_4,
            'ФИО': read_5,
            'Дата рождения': read_6,
            'Место рождения': read_7,
            'Пол': read_8
        })

        with open('Processing/data_delete.json', 'w', encoding='utf-8') as outfile: # запись и перезапись русского шаблона
            json.dump(data_display, outfile, indent=4, ensure_ascii=False)
        with open('Processing/data_delete.json', 'r',encoding='utf-8') as file:
            data = file.read()
            self.ui.load_data.setText(data)

        data = {}  # шаблон для JSON который будет использоваться для парсинга на сайте
        data['passport_recognition'] = []
        data['passport_recognition'].append({
            'pas_issue': read_1,
            'date_issue': read_2,
            'division_code': read_3,
            'num_pasp': read_4,
            'fio': read_5,
            'date_birth': read_6,
            'place_birth': read_7,
            'sex': read_8
        })

        with open('JSON/data.json', 'w', encoding='utf-8') as outfile: # запись в файл
            json.dump(data, outfile, indent=4, ensure_ascii=False)

        files = glob.glob('Temp/*')  # очистка папок Temp и Processing, чтобы не занимать место посел обработки, а также нельзя было простмореть эти данные
        for f in files:
            os.remove(f)
        files = glob.glob('Processing/*')
        for f in files:
            os.remove(f)

    def file_path(self): # функция получения пути фото
        if not os.path.isdir("Temp"): #Если папка отсутвует в программе, то создать
            os.mkdir("Temp")
        if not os.path.isdir("Processing"): #Если папка отсутвует в программе, то создать
            os.mkdir("Processing")
        file_path_read = QFileDialog.getOpenFileName(self)[0]  # откртие проводника
        with open('Processing/process.txt', 'w', encoding='utf-8') as f: # запись пути в файл
            f.write(file_path_read)

    def directore_open(self): # функция открытия JSON
        path = "JSON"
        path = os.path.realpath(path)
        os.startfile(path)









def main():
    app = QtWidgets.QApplication([])  # функции работы дизайна
    application = PassportEye() # передаем наши правила оформелния дизайна
    application.show()  # открытие программы
    sys.exit(app.exec_()) #закрытие программы

if __name__ == '__main__': # по стилистике и правилам оформления указываем main в которую занесены основные функции
    main()
