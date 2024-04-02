# my_application.py
import numpy
import time

from generalapi.host import QHost
from generalapi.qthread_event import QThreadEvent

from PyQt5.QtWidgets import QApplication, QPushButton
from PyQt5.QtCore import QThread, pyqtSlot, pyqtSignal, QObject, QWaitCondition, QMutex

import configparser
import sys


class MyApplication(QPushButton):

    sig = pyqtSignal()

    def __init__(self):
        super(MyApplication, self).__init__("TEST")
        event = QThreadEvent(self)
        ip, port = "localhost", 12340
        app_root = self
        self.ssl_host = QHost(self, ip, port, app_root, event)
        self.ssl_host.start()

        self.__foo = "__foo variable"
        self.bar = "bar variable"
        self.my_tuple = (1, 2, 3)
        self.main_thread = self.thread()
        self.t = QThread(self)
        self.t.run = self.mutex_unlock
        self.condition = QWaitCondition()
        self.mutex = QMutex()
        # self.sig.connect(self.mutex_unlock)
        self.clicked.connect(self.test)
        self.cp = configparser.ConfigParser()
        config_dict = {
            'Section1': {
                'key1': 'value1',
                'key2': 'value2'
            },
            'Section2': {
                'key3': 'value3',
                'key4': 'value4'
            }
        }
        # Populate the configparser object with the dictionary
        for section, options in config_dict.items():
            self.cp.add_section(section)
            for key, value in options.items():
                self.cp.set(section, key, value)
        self.arr = numpy.zeros((10, 10))

    @pyqtSlot()
    def mutex_unlock(self):
        print "mutex unlock"
        time.sleep(5)
        self.condition.wakeAll()
        print "unlocked"

    @pyqtSlot()
    def test(self):
        print self.thread() == self.main_thread
        return self.thread() == self.main_thread    # test if host executes the command in main thread

    def test_thread(self):
        self.t.start()
        self.mutex.lock()
        print "waiting"
        try:
            self.condition.wait(self.mutex)
        finally:
            self.mutex.unlock()
        print "wait complete"
        return 0

    @property
    def foo(self):
        return self.__foo

    def baz(self):
        return "baz called"

    def sum(self, *args):
        print("sum called", args)
        return sum(args)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    r = MyApplication()
    r.show()
    app.exec_()
