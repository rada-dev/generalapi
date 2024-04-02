# my_api.py
import time

from generalapi.client import Client


class MyAPI(Client):

    def __init__(self):
        ip, port = "localhost", 12340
        super(MyAPI, self).__init__(ip, port)
        self.connect()

    @property
    def foo(self):
        return self.exec_("foo")  # exec MyApplication.foo

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

    def test(self):
        return self.exec_("test")

    def test_thread(self):
        return self.exec_("test_thread")

    @property
    def cp(self):
        return self.exec_("cp")

    @property
    def arr(self):
        return self.exec_("arr")


if __name__ == '__main__':
    api = MyAPI()
    print(api.foo)
    print(api.bar)
    print(api.my_tuple)
    print(api.baz())
    print(api.sum(3.14, 2.71))
    print(api.cp.get("Section2", "key3"))
    print(api.arr)
    # print(api.test())
    # print(api.test_thread())
    api.close()
