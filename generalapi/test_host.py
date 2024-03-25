import host
import threading


class Root(object):

    def a(self, *args, **kwargs):
        print "a"
        return "a"

    def b(self, *args, **kwargs):
        print "b"
        return "b"


if __name__ == '__main__':
    r = Root()
    e = threading.Event()
    e.set()
    h = "localhost", 12340
    h = host.Host(r, h, e)
