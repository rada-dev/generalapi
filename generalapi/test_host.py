# my_application.py
import numpy
import time

from generalapi.host import QHost
from generalapi.qthread_event import QThreadEvent

from PyQt5.QtWidgets import QApplication, QPushButton
from PyQt5.QtCore import QThread, pyqtSlot, pyqtSignal, QObject, QWaitCondition, QMutex

import configparser
import sys


class AcqThread(QThread):

    error = pyqtSignal(str)

    def __init__(self, parent):
        super(AcqThread, self).__init__(parent)
        self.cond = QWaitCondition()
        self.mutex = QMutex()
        self.__finish_signal = None
        self.__acq_method = None

    def init(self):
        try:
            self.started.disconnect()
        except TypeError:
            pass
        try:
            self.finished.disconnect()
        except TypeError:
            pass
        if self.__finish_signal is not None:
            try:
                self.__finish_signal.disconnect(self.cond.wakeAll)
            except TypeError:
                pass
        self.__finish_signal = None
        self.__acq_method = None

    def start(self, priority=None):
        if self.__finish_signal is not None and self.__acq_method is not None:
            self.__finish_signal.connect(self.cond.wakeAll)
            super(AcqThread, self).start()
            print "acq thread started",
        else:
            print "Finish signal or acq method not set!"
            self.error.emit("Finish signal or acq method not set!")

    def setFinishSignal(self, signal):
        self.__finish_signal = signal

    def setAcqMethod(self, method):
        self.__acq_method = method

    def run(self):
        print "acq thread calling acq method", self.__acq_method
        self.__acq_method()
        print "acq thread acq method called"
        self.mutex.lock()
        try:
            self.cond.wait(self.mutex)
        finally:
            self.mutex.unlock()
        print "acq thread finished"


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
        self.acq_thread = AcqThread(self)
        self.acq_thread.setAcqMethod(self.acq_method)
        self.acq_thread.setFinishSignal(self.sig)
        self.unlock_thread = QThread(self)
        self.unlock_thread.run = self.mutex_unlock
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
        self.arr = numpy.eye(10)

    @pyqtSlot()
    def mutex_unlock(self):
        print "mutex unlock"
        time.sleep(5)
        self.sig.emit()
        print "unlocked"

    @pyqtSlot()
    def acq_method(self):
        time.sleep(0.1)

    @pyqtSlot()
    def test(self):
        print self.thread() == self.main_thread
        self.acq_thread.start()
        self.unlock_thread.start()
        return self.thread() == self.main_thread    # test if host executes the command in main thread

    def test_thread(self):
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
