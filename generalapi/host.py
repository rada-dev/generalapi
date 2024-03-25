import threading
import socket
import common
import cPickle as pickle


class Host(object):

    MAX_CLIENTS = 1
    TIMEOUT_ACCEPT = 0.5

    MSGLEN_NBYTES = 4

    def __init__(self, root, hostname, threading_event):
        self.root = root
        self.hostname = hostname
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # create a uds/tcp socket
        self.threading_event = threading_event
        self.thread_accept = threading.Thread(target=self.accept)
        self.thread_accept.start()
        self.threads_conn = {}

    @property
    def running(self):
        return self.threading_event.is_set()

    def accept(self):
        self.sock.bind(self.hostname)
        self.sock.listen(self.MAX_CLIENTS)  # listen for incoming connections
        self.sock.settimeout(self.TIMEOUT_ACCEPT)
        while self.running:
            try:
                conn, hostname = self.sock.accept()
                conn.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                t = threading.Thread(target=self.recv, args=(conn,))
                self.threads_conn[conn] = t
                t.start()

            # exception handling while communicating
            except socket.timeout:
                # print("socket accept timeout", file=sys.stderr)
                continue
        self.sock.close()

    def recv(self, conn):
        while self.running:
            try:
                recv_len_bytes = conn.recv(self.MSGLEN_NBYTES)
                if recv_len_bytes:
                    recv_len = common.int_from_bytes(recv_len_bytes)  # receive packet
                    pickled_msg = conn.recv(recv_len)
                    command, args, kwargs = pickle.loads(pickled_msg)
                    method = getattr(self.root, command)
                    ret = method(args, kwargs)
                    pickled_ret = pickle.dumps(ret)
                    ret_len_bytes = common.int_to_bytes(len(pickled_ret))
                    conn.send(ret_len_bytes)
                    conn.send(pickled_ret)
            except socket.timeout:
                continue
        self.threads_conn.pop(conn)
