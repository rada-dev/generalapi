# my_application.py
from generalapi.host import QHost
from generalapi.qthread_event import QThreadEvent
from PyQt5.QtWidgets import QApplication, QMainWindow
import sys


class MyApplication(QMainWindow):

    def __init__(self):
        super(MyApplication, self).__init__()
        event = QThreadEvent(self)
        ip, port = "localhost", 12340
        app_root = self
        self.ssl_host = QHost(self, ip, port, app_root, event)
        self.ssl_host.start()

        self.__foo = "__foo variable"
        self.bar = "bar variable"
        self.my_tuple = (1, 2, 3)

    @property
    def foo(self):
        return self.__foo

    def baz(self):
        print("baz called")
        return "baz called"

    def sum(self, *args):
        print("sum called", args)
        return sum(args)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    r = MyApplication()
    app.exec_()
