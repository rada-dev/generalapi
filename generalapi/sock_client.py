import socket
import common


class SockClient(object):

    TIMEOUT = None

    MSGLEN_NBYTES = 4

    def __init__(self, sock, hostname):
        self.hostname = hostname
        self.sock = sock
        self.sock.settimeout(self.TIMEOUT)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def connect(self):
        self.sock.connect(self.hostname)

    def close(self):
        self.sock.shutdown(socket.SHUT_RDWR)
        self.sock.close()

    def exec_(self, command, *args, **kwargs):
        common.pack_and_send(self.sock, (command, args, kwargs))
        recv_len_bytes = self.sock.recv(self.MSGLEN_NBYTES)
        return common.recv_and_unpack(self.sock, recv_len_bytes)
