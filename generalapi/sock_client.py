import socket
import pickle
import common


class SockClient(object):

    TIMEOUT = 0.5

    MSGLEN_NBYTES = 4

    def __init__(self, sock, hostname):
        self.hostname = hostname
        self.sock = sock
        self.sock.settimeout(self.TIMEOUT)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def connect(self):
        self.sock.connect(self.hostname)

    def close(self):
        self.sock.close()

    def exec_(self, command, *args, **kwargs):
        pickled_cmd = pickle.dumps((command, args, kwargs))
        cmd_len = common.int_to_bytes(len(pickled_cmd))
        self.sock.send(cmd_len)
        self.sock.send(pickled_cmd)
        recv_len = common.int_from_bytes(self.sock.recv(self.MSGLEN_NBYTES))  # receive packet
        pickled_ret = self.sock.recv(recv_len)
        ret = pickle.loads(pickled_ret)
        return ret
