import host
import threading
import os


class MyApplication(object):

    def __init__(self):
        event = threading.Event()
        ip, port = "localhost", 12340
        self.host = host.Host(ip, port, self, event)
        self.host.start()

        keyfile = os.path.join("test_cert", "keyfile.key")
        certfile = os.path.join("test_cert", "certfile.crt")
        ip, port = "localhost", 12341
        self.ssl_host = host.SSLHost(ip, port, self, event, keyfile, certfile)
        self.ssl_host.start()

        self.__foo = "__foo variable"
        self.bar = "bar variable"
        self.my_tuple = (1, 2, 3)

    @property
    def foo(self):
        return self.__foo

    def baz(self):
        print "baz called"
        return "baz called"

    def sum(self, *args):
        print "sum called", args
        return sum(args)


if __name__ == '__main__':
    r = MyApplication()

