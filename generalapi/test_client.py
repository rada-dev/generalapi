import client
import threading


if __name__ == '__main__':
    h = "localhost", 12340
    e = threading.Event()
    e.set()
    c = client.Client(h, e)
    print c.exec_("a")
    print c.exec_("b")
    print c.exec_("v")
    print c.exec_("p")
    print c.exec_("s", 4, 5)
