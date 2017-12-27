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
        self.ex = None
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
        if len(self.check_points) > 1:
            self.ex = self.check_points[-2]

    def report(self):
        rep = dict()
        if len(self.check_points) > 1:
            rep['name'] = self.name
            rep['CPs'] = {'num': len(self.check_points), 'str': str(len(self.check_points))}
            rep['bytes'] = {'now': self.now.bytes, 'ex': self.ex.bytes,
                            'out': tostring(self.now.bytes, self.ex.bytes, 'B')}
            rep['lines'] = {'now': self.now.lines, 'ex': self.ex.lines,
                            'out': tostring(self.now.lines, self.ex.lines)}
            rep['classes'] = {'now': self.now.classes, 'ex': self.ex.classes,
                              'out': tostring(self.now.classes, self.ex.classes)}
            rep['methods'] = {'now': self.now.methods, 'ex': self.ex.methods,
                              'out': tostring(self.now.methods, self.ex.methods)}
            rep['functions'] = {'now': self.now.functions, 'ex': self.ex.functions,
                                'out': tostring(self.now.functions, self.ex.functions)}
        else:
            rep['name'] = self.name + '(new)'
            rep['CPs'] = {'num': len(self.check_points), 'str': str(len(self.check_points))}
            rep['bytes'] = {'now': self.now.bytes, 'ex': 0, 'out': tostring(self.now.bytes, None, 'B')}
            rep['lines'] = {'now': self.now.lines, 'ex': 0, 'out': tostring(self.now.lines, None)}
            rep['classes'] = {'now': self.now.classes, 'ex': 0, 'out': tostring(self.now.classes, None)}
            rep['methods'] = {'now': self.now.methods, 'ex': 0, 'out': tostring(self.now.methods, None)}
            rep['functions'] = {'now': self.now.functions, 'ex': 0, 'out': tostring(self.now.functions, None)}
        return rep


def tostring(now, old, additive=''):
    #Передевать в 'новое_значение(старое_значение +-разница | -+разница_в_вроцентах)'
    if old is None or now - old == 0:
        old = ''
    else:
        old = now - old
        sign = ''
        if old > 0:
            sign = '+'
        elif old < 0:
            sign = '-'
        old = abs(old)
        if old > 999:
            old = sign + str(round(old / 1000, len(str(old)) - 3)) + 'K' + additive
        else:
            old = sign + str(old) + additive
        old = '({})'.format(old)
    if now > 999:
        now = str(round(now / 1000, len(str(now)) - 3)) + 'K' + additive
    else:
        now = str(now) + additive
    return now + old


def report():
    data = []
    for f in files:
        data.append(f.report())
    end = dict()
    end['name'] = len(data)
    end['cp'] = max(map(lambda x: x['CPs']['num'], data))
    end['size'] = tostring(sum(map(lambda x: x['bytes']['now'], data)), sum(map(lambda x: x['bytes']['ex'], data)), 'B')
    end['lines'] = tostring(sum(map(lambda x: x['lines']['now'], data)), sum(map(lambda x: x['lines']['ex'], data)))
    end['classes'] = tostring(sum(map(lambda x: x['classes']['now'], data)),
                              sum(map(lambda x: x['classes']['ex'], data)))
    end['methods'] = tostring(sum(map(lambda x: x['methods']['now'], data)),
                              sum(map(lambda x: x['methods']['ex'], data)))
    end['functions'] = tostring(sum(map(lambda x: x['functions']['now'], data)),
                                sum(map(lambda x: x['functions']['ex'], data)))
    widch = dict()
    widch['name'] = max(max(map(lambda x: len(x['name']), data)), 4)
    widch['cp'] = max(max(map(lambda x: len(x['CPs']['str']), data)), 3)
    widch['size'] = max(max(map(lambda x: len(x['bytes']['out']), data)), 4, len(end['size']))
    widch['lines'] = max(max(map(lambda x: len(x['lines']['out']), data)), 5, len(end['lines']))
    widch['classes'] = max(max(map(lambda x: len(x['classes']['out']), data)), 7, len(end['classes']))
    widch['methods'] = max(max(map(lambda x: len(x['methods']['out']), data)), 7, len(end['methods']))
    widch['functions'] = max(max(map(lambda x: len(x['functions']['out']), data)), 9, len(end['functions']))

    zero = '} | {:>'.join(list(map(lambda x: str(widch[x]), widch)))
    zero = '{:>' + zero + '}'
    frame = '\n' + '+'.join(list(map(lambda x: '-' * (widch[x] + 2), widch)))[1: -1] + '\n'
    return frame.join((zero.format('name', 'CP', 'size', 'lines', 'classes', 'methods', 'functions'),
                       '\n'.join(map(lambda x: zero.format(x['name'], x['CPs']['str'], x['bytes']['out'],
                                                          x['lines']['out'], x['classes']['out'],
                                                          x['methods']['out'], x['functions']['out']), data)),
                      zero.format('all', 'max', 'sum', 'sum', 'sum', 'sum', 'sum'),
                      zero.format(end['name'], end['cp'], end['size'], end['lines'],
                                  end['classes'], end['methods'], end['functions'])))


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
