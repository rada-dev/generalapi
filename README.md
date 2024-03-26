# generalapi

openssl req -x509 -sha256 -nodes -days 365 -newkey rsa:2048 -keyout keyfile.key -out certfile.crt

```python 
# main.py
from generalapi import host
import threading


class Root(object):

    def __init__(self):
        event = threading.Event()
        event.set()
        hostname = "localhost", 12340
        self.host = host.Host(self, hostname, event)
        self.__p = 1
        self.v = 2

    @property
    def p(self):
        return self.__p

    def a(self):
        print "a"
        return "a"

    def b(self):
        print "b"
        return "b"

    def s(self, *args):
        print "sum", args
        return sum(args)


if __name__ == '__main__':
    r = Root()
```

```python 
# client.py
from generalapi import client
import threading


if __name__ == '__main__':
    h = "localhost", 12340
    e = threading.Event()
    e.set()
    c = client.Client(h, e)
    print c.exec_("a")
    # a
    print c.exec_("b")
    # b
    print c.exec_("v")
    # 2
    print c.exec_("p")
    # 1
    print c.exec_("s", 4, 5)
    # 9
```