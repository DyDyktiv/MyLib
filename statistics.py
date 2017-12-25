import os
import re
import os.path
import time


re_extension = re.compile('.+\.py[w]?')
re_class = re.compile('[ ]*class ')
re_method = re.compile('[ ]+def ')
re_function = re.compile('def ')

files = []


class Record:
    #Переделать класс в виде словаря, убрать класс
    def __init__(self, mtime, fsize, lines, classes, methods, functions):
        self.time = mtime
        self.bytes = fsize
        self.lines = lines
        self.classes = classes
        self.methods = methods
        self.functions = functions


class Pile:
    def __init__(self, name):
        self.name = name
        self.now = None
        self.check_points = []
        self.check_point()

    def check_point(self):
        mtime = int(time.time())
        if os.path.exists(self.name):  # Проверка на наличие файла.
            fsize = os.path.getsize(self.name)  # Размер файла в байтах.
            lines = 0
            classes = 0
            methods = 0
            functions = 0
            f = open(self.name, encoding='utf-8')
            for s in f:
                lines += 1
                classes += int(bool(re_class.match(s)))
                methods += int(bool(re_method.match(s)))
                functions += int(bool(re_function.match(s)))
            f.close()
            #Научить проверять на одинаковые подряд идущие записи и перезаписывать время в последней такой
            self.check_points.append(Record(mtime, fsize, lines, classes, methods, functions))
        else:
            self.check_points.append(Record(mtime, None, None, None, None, None))
        self.now = self.check_points[-1]

    def report(self):
        rep = {'name': self.name, 'CPs': len(self.check_points)}
        if len(self.check_points) > 1:
            pass
        else:
            rep['bytes'] = {'now': self.now.bytes, 'delta': 0, 'out': fufu(self.now.bytes, None, 'B')}
        return report


def fufu(now, old, additive=''):
    #Передевать в 'новое_значение(старое_значение +-разница | -+разница_в_вроцентах)'
    if old is None:
        old = 'new'
    else:
        old = now - old
        if old == 0:
            old = ''
        else:
            sign = ''
            if old > 0:
                sign = '+'
            elif old < 0:
                sign = '-'
            if abs(old) > 999:
                old = sign + str(round(old, 3 - len(str(old)))) + 'K' + additive
            else:
                old = sign + str(old) + additive
            old = '({})'.format(old)
    if now > 999:
        now = str(round(now, 3 - len(str(now)))) + 'K' + additive
    else:
        now = str(now) + additive
    return now + old


def report():
    return 0


def started():
    global files
    if os.path.exists('statistics.txt'):  # Проверка на наличие файла статистики.
        pass
    else:
        pass
    current_files = os.listdir(os.getcwd())
    #Удалить файл статистики из отслеживания
    current_files = list(filter(lambda x: re_extension.match(x), current_files))
    for f in files:
        if f in current_files:
            current_files.remove(f)
    current_files = list(map(lambda x: Pile(x), current_files))
    files.extend(current_files)
    print(report())


started()
#input()
#Добавить сохранение и загрузку статистики из фалйа. JSON
