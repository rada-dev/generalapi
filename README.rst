Socket communication interface to create custom API
==========================================================

Installation:
-------------

.. code::

    pip install -r requirements.txt
    python setup.py sdist
    pip install sdist/generalapi-*.tar.gz

Various sockets may be used:
----------------------------

1. plain (no encryption)
2. SSL (with encryption)
3. UDS (unix domain socket)

1. Plain socket (no encryption) example:
----------------------------------------

.. code::

    # my_application.py
    from generalapi.host import Host
    import threading


    class MyApplication(object):

        def __init__(self):
            event = threading.Event()
            ip, port = "localhost", 12340
            app_root = self     # self.something will be called by client
            self.host = Host(ip, port, app_root, event)
            self.host.start()

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

.. code::

    # my_api.py
    from generalapi.client import Client


    class MyAPI(Client):

        def __init__(self):
            ip, port = "localhost", 12340
            super(MyAPI, self).__init__(ip, port)
            self.connect()

        @property
        def foo(self):
            return self.exec_("foo")    # exec MyApplication.foo

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

2. SSL socket (encrypted) example:
----------------------------------

Create SSL keyfile and certfile

.. code::

    openssl req -x509 -sha256 -nodes -days 365 -newkey rsa:2048 -keyout keyfile.key -out certfile.crt

.. code::

    # my_application.py
    from generalapi.host import SSLHost
    import threading
    import os


    class MyApplication(object):

        def __init__(self):
            event = threading.Event()
            keyfile = os.path.join("test_cert", "keyfile.key")
            certfile = os.path.join("test_cert", "certfile.crt")
            ip, port = "localhost", 12340
            app_root = self     # self.something will be called by client
            self.ssl_host = SSLHost(ip, port, app_root, event, keyfile, certfile)
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

.. code::

    # my_api.py
    from generalapi.client import SSLClient
    import os


    class MyAPI(SSLClient):

        def __init__(self):
            keyfile = os.path.join("test_cert", "keyfile.key")
            certfile = os.path.join("test_cert", "certfile.crt")
            ip, port = "localhost", 12340
            super(MyAPI, self).__init__(ip, port, keyfile, certfile)
            self.connect()

        @property
        def foo(self):
            return self.exec_("foo")    # exec MyApplication.foo

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

3. UDS (unix domain socket) example:
------------------------------------

.. code::

    # my_application.py
    from generalapi.host import UDSHost
    import threading


    class MyApplication(object):

        def __init__(self):
            event = threading.Event()
            uds_path = "/tmp/stream.sock"
            app_root = self     # self.something will be called by client
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

.. code::

    # my_api.py
    from generalapi.client import UDSClient


    class MyAPI(UDSClient):

        def __init__(self):
            uds_path = "/tmp/stream.sock"
            super(MyAPI, self).__init__(uds_path)
            self.connect()

        @property
        def foo(self):
            return self.exec_("foo")    # exec MyApplication.foo

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
