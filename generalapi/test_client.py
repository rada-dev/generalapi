import time

import client
import os


if __name__ == '__main__':
    ip, port = "localhost", 12340
    c = client.Client(ip, port)
    c.connect()
    print c.exec_("a")
    print c.exec_("b")
    print c.exec_("v")
    time.sleep(10)
    print c.exec_("p")
    print c.exec_("s", 4, 5)
    c.close()

    ip, port = "localhost", 12341
    keyfile = os.path.join("test_cert", "keyfile.key")
    certfile = os.path.join("test_cert", "certfile.crt")
    c_ssl = client.SSLClient(ip, port, keyfile, certfile)
    c_ssl.connect()
    print c_ssl.exec_("a")
    print c_ssl.exec_("b")
    print c_ssl.exec_("v")
    time.sleep(10)
    print c_ssl.exec_("p")
    print c_ssl.exec_("s", 4, 5)
    c_ssl.close()
