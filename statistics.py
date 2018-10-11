import os
import os.path
import re
import time


def scanning(path=os.getcwd(), homepath='', depth=-1):
    """RU:
        Рекурсивная функция, сканирующая вглубь переданного пути и \возвращающая список файлов с раширение .py[w].
        Если depth = -1:
            то бесконечное погружение
        если 0:
            без погружения
        иначе на укажанную глубину.
    EN:
        Recursive function that scans deep into the transmitted path and returns a list of files .py[w]
        If depth = -1:
            endless immersion
        elif depth = 0:
            then not immersion
        else:
            by a specified number"""
    fds = os.listdir(path)  # fds = files and dirs
    ds = []  # dirs for immersion
    dpyfiles = []  # list of .py files
    repy = re.compile('.+\.py[wd]?$')

    for fileordir in fds:
        if repy.match(fileordir):
            dpyfiles.append(os.path.join(homepath, fileordir))  # Check for .py file
        if os.path.isdir(os.path.join(path, fileordir)):
            ds.append(fileordir)
    del fds

    if depth != 0:
        for storage in ds:
            dpyfiles.extend(scanning(os.path.join(path, storage),
                                     os.path.join(homepath, storage),
                                     depth - 1))

    if os.path.join(homepath, os.path.split(__file__)[1]) in dpyfiles:
        if os.path.samefile(__file__, os.path.join(path, os.path.split(__file__)[1])):
            dpyfiles.remove(os.path.join(homepath, os.path.split(__file__)[1]))
    return dpyfiles


class Pyfile:
    def __init__(self, name):
        self.name = name
        self.checks = []
        self.scan()

    def scan(self):
        if os.path.exists(self.name):
            size = os.path.getsize(self.name)
            with open(self.name, encoding='utf-8') as file:
                classes = 0
                defines = 0
                lines = 0
                for line in file:
                    if re.match(r'[\t]*class ', line):
                        classes += 1
                    if re.match(r'[\t]*def ', line):
                        defines += 1
                    lines += 1
                self.checks.append(CheckPoint(time.time(), classes, defines, lines, size))
        else:
            self.checks.append(CheckPoint(time.time()))


class CheckPoint:
    def __init__(self, date, classes=0, defines=0, lines=0, sizes=0):
        self.date = date
        self.classes = classes
        self.defines = defines
        self.lines = lines
        self.bytes = sizes


if __name__ == '__main__':
    pyfiles = scanning()
    for fp in pyfiles:
        Pyfile(fp)
    input()
