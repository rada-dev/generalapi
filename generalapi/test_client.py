import time

from generalapi.client import Client
import os


class MyAPI(Client):

    ip, port = "localhost", 12340

    def __init__(self):
        super(MyAPI, self).__init__(self.ip, self.port)
        self.connect()

    @property
    def foo(self):
        return self.exec_("foo")

    @property
    def bar(self):
        return self.exec_("bar")

    @property
    def my_tuple(self):
        return self.exec_("my_tuple")

    def baz(self):
        return self.exec_("baz")

    def sum(self, x, y):
        return self.exec_("sum", x, y)


if __name__ == '__main__':

    api = MyAPI()
    print(api.foo)
    print(api.bar)
    print(api.my_tuple)
    print(api.baz())
    print(api.sum(3.14, 2.71))
    api.close()

    # ip, port = "localhost", 12341
    # keyfile = os.path.join("test_cert", "keyfile.key")
    # certfile = os.path.join("test_cert", "certfile.crt")
    # c_ssl = client.SSLClient(ip, port, keyfile, certfile)
    # c_ssl.connect()
    # print(c_ssl.exec_("a")
    # print(c_ssl.exec_("b")
    # print(c_ssl.exec_("v")
    # time.sleep(10)
    # print(c_ssl.exec_("p")
    # print(c_ssl.exec_("s", 4, 5)
    # c_ssl.close()
