# my_application.py
from generalapi.host import UDSHost
import threading


class MyApplication(object):

    def __init__(self):
        event = threading.Event()
        uds_path = "test_uds"
        app_root = self
        self.ssl_host = UDSHost(uds_path, app_root, event)
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
    r = MyApplication()