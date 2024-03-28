# my_api.py
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


if __name__ == '__main__':
    api = MyAPI()
    print(api.foo)
    print(api.bar)
    print(api.my_tuple)
    print(api.baz())
    print(api.sum(3.14, 2.71))
    api.close()
