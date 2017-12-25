import re
import time
from os import chdir
import xlwt
import xlrd


re_atr = re.compile('[A-Z]{2,3}[\d]{4}[A-Z]{3}')
slprint = 'ID: {} PRJ: {}({}-{}) MAT: {}({}-{}) M: {}/{} G: {}/{}'
ft = ('F', 'T')
ds = {}   # DetailS


class Detail:
    def __init__(self, n, art):
        self.id = n
        self.art = art
        self.project_new = False
        self.project_old = False
        self.project_out = False
        self.matrix_new = 0
        self.matrix_old = False
        self.matrix_out = 0
        self.made_new = 0
        self.made_old = 0
        self.made_out = 0
        self.given_new = 0
        self.given_old = 0
        self.given_out = 0

    def rise(self, mod, mat, mad, giv):
        self.project_old = max(mod, self.project_old)
        self.matrix_old = max(mat, self.matrix_old)
        self.made_old += mad
        self.given_old += giv

    def analize(self):
        """
        Производит сравнение новых и выведенных в отчет данных
        :return: True or False
        """
        self.project_out = bool(self.project_new - self.project_old)
        if self.matrix_old is True:
            self.matrix_out = 0
        else:
            self.matrix_out = self.matrix_new
        self.made_out = self.made_new - self.made_old
        self.given_out = self.given_new - self.given_old
        if self.project_out or self.matrix_out or self.made_out or self.given_out:
            return True
        else:
            return False

    def lprint(self):
        print(slprint.format(self.id, self.project_out, self.project_new, self.project_old,
                             self.matrix_out, self.matrix_new, self.matrix_old,
                             self.made_new, self.made_old, self.given_new, self.given_old))


def read_assistent():
    global ds
    rb = xlrd.open_workbook('D:/YandexDisk/Документы/Петр/Assistent.xlsx')
    sheet = rb.sheet_by_index(0)
    for rownum in range(1, sheet.nrows):
        line = sheet.row_values(rownum)
        key = line[1]
        ds[key] = Detail(int(line[0]), key)
        ds[key].project_new = bool(line[12])
        if line[13] == 'P':
            ds[key].matrix_new = 2
        elif line[13] == 1.0:
            ds[key].matrix_new = 1
        else:
            ds[key].matrix_new = 0
        ds[key].made_new = int([0, line[14]][bool(line[14])])
        ds[key].given_new = int([0, line[15]][bool(line[15])])


def read_report():
    global ds
    rb = xlrd.open_workbook('D:/YandexDisk/Документы/Петр/Report.xlsx')
    sheet = rb.sheet_by_index(0)
    for rownum in range(0, sheet.nrows):
        line = sheet.row_values(rownum)
        if re_atr.match(str(line[0])):
            key = line[0]
            project = bool(line[1])
            matrix = bool(line[2])
            made = int(line[3])
            given = int(line[4])
            ds[key].rise(project, matrix, made, given)


def write():
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Лист1')

    ws.write(0, 0, 'Артикул')
    ws.write(0, 1, 'Проект')
    ws.write(0, 2, 'Исполнение')
    ws.write(0, 3, 'Сделано')
    ws.write(0, 4, 'Отгружено')

    i = 1
    pds = tuple(filter(lambda x: ds[x].analize(), ds))
    for det in pds:
        ds[det].analize()
        ws.write(i, 0, ds[det].art)
        ws.write(i, 1, ('', '+')[ds[det].project_out])
        ws.write(i, 2, ('', '+', 'Petr')[ds[det].matrix_out])
        ws.write(i, 3, ('', ds[det].made_out)[bool(ds[det].made_out)])
        ws.write(i, 4, ('', ds[det].given_out)[bool(ds[det].given_out)])
        i += 1

    i += 1
    ws.write(i, 0, 'Итого на {}:'.format(time.strftime('%d.%m.%Y')))
    i += 1
    ws.write(i, 1, xlwt.Formula('COUNTIF(B2:B{};"+")'.format(i-2)))
    ws.write(i, 2, xlwt.Formula('COUNTIF(C2:C{};"+")'.format(i-2)))
    ws.write(i, 3, xlwt.Formula('sum(D2:D{})'.format(i-2)))
    i += 1
    ws.write(i, 0, 'Стоимость')
    ws.write(i, 1, 400)
    ws.write(i, 2, 450)
    ws.write(i, 3, 25)
    ws.write(i, 6, 'ИТОГО')
    i += 1
    ws.write(i, 0, 'Итого')
    ws.write(i, 1, xlwt.Formula('B{}*B{})'.format(i - 1, i)))
    ws.write(i, 2, xlwt.Formula('C{}*C{}'.format(i - 1, i)))
    ws.write(i, 3, xlwt.Formula('D{}*D{}'.format(i - 1, i)))
    ws.write(i, 6, xlwt.Formula('sum(B{0}:D{0})'.format(i + 1)))

    chdir('D:/YandexDisk/Документы/Петр/')
    wb.save(time.strftime('Report %d.%m.%Y.xls'))


read_assistent()
read_report()
write()
