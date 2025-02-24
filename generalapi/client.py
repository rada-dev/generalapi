from sock_client import SockClient
import socket
import ssl


class Client(SockClient):

    def __init__(self, ip, port):
        hostname = (ip, port)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        super(Client, self).__init__(sock, hostname)


class SSLClient(SockClient):

    def __init__(self, ip, port, keyfile, certfile, protocol=ssl.PROTOCOL_TLSv1_2):
        hostname = (ip, port)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ssl_sock = ssl.wrap_socket(sock, keyfile=keyfile, certfile=certfile, ssl_version=protocol)
        super(SSLClient, self).__init__(ssl_sock, hostname)


class UDSClient(SockClient):

    def __init__(self, hostname):
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        super(UDSClient, self).__init__(sock, hostname)


if __name__ == '__main__':
    c = Client("localhost", 18813)
    c.connect()
    print c.exec_("a")
    print c.exec_("b", 1, 2)
