import host
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

