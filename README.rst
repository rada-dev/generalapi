Python socket communication interface to create custom API
==========================================================

Installation:
-------------

.. code::

    pip install -r requirements.txt
    python setup.py sdist
    pip install sdist/generalapi-*.tar.gz

Features:
---------

- host and client interfaces with use of:

1. plain socket (no encryption)

.. code::

    from generalapi.host import Host
    from generalapi.client import Client

2. SSL socket (with encryption)

.. code::

    from generalapi.host import SSLHost
    from generalapi.client import SSLClient

3. UDS (unix domain socket)

.. code::

    from generalapi.host import UDSHost
    from generalapi.client import UDSClient

4. PyQt integration

    if you used the client to execute host commands which, for instance, create and handle another QThreads, you may experience the host command not being executed

    in such cases PyQt compatible host is needed, with this, the commands will be executed in the application main thread, not in the thread which does socket.recv()

.. code::

    # host variants with QThread
    from generalapi.host import QHost   # host which employs QThread (plain socket)
    from generalapi.host import QSSLHost   # host which employs QThread (SSL socket)
    from generalapi.host import QUDSHost   # host which employs QThread (UDS socket)
    # client side will be the same
    from generalapi.client import Client

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


4. QHost example:
-----------------

.. code::

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
            self.main_thread = self.thread()

        def test(self):
            return self.thread() == self.main_thread    # test if host executes the command in main thread

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
