from sock_host import SockHost
import socket
import ssl


class Host(SockHost):

    def __init__(self, ip, port, root, threading_event):
        hostname = ip, port
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        super(Host, self).__init__(sock, hostname, root, threading_event)


class SSLHost(SockHost):

    def __init__(self, ip, port, root, threading_event, keyfile, certfile, protocol=ssl.PROTOCOL_TLSv1_2):
        hostname = ip, port
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # create a uds/tcp socket
        ssl_sock = ssl.wrap_socket(sock, keyfile=keyfile, certfile=certfile, ssl_version=protocol, server_side=True)
        self.keyfile = keyfile
        self.certfile = certfile
        super(SSLHost, self).__init__(ssl_sock, hostname, root, threading_event)


class UDSHost(SockHost):

    def __init__(self, hostname, root, threading_event):
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        super(UDSHost, self).__init__(sock, hostname, root, threading_event)
