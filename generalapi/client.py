import socket
import pickle
import common


class Client(object):

    MAX_CLIENTS = 1
    TIMEOUT_ACCEPT = 0.5

    MSGLEN_NBYTES = 4

    COMMANDS = [

    ]

    def __init__(self, hostname, threading_event):
        self.hostname = hostname
        self.threading_event = threading_event
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # create a tcp/ip socket
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.connect(self.hostname)

    @property
    def running(self):
        return self.threading_event.is_set()

    def exec_(self, command, *args, **kwargs):
        pickled_cmd = pickle.dumps((command, args, kwargs))
        cmd_len = common.int_to_bytes(len(pickled_cmd))
        self.sock.send(cmd_len)
        self.sock.send(pickled_cmd)
        recv_len = common.int_from_bytes(self.sock.recv(self.MSGLEN_NBYTES))  # receive packet
        pickled_ret = self.sock.recv(recv_len)
        ret = pickle.loads(pickled_ret)
        return ret
