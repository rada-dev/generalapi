import ssl
import threading
import socket
import common


class SockHost(object):

    MAX_CLIENTS = 10
    TIMEOUT = 0.5

    MSGLEN_NBYTES = 4

    def __init__(self, sock, hostname, root, threading_event):
        self.sock = sock
        self.root = root
        self.hostname = hostname
        self.threading_event = threading_event
        self.thread_accept = threading.Thread(target=self.accept)
        self.threads_conn = {}

    def start(self):
        self.threading_event.set()
        self.thread_accept.start()

    def stop(self):
        self.threading_event.clear()
        self.thread_accept.join()
        for t in self.threads_conn.values():
            t.join()

    @property
    def running(self):
        return self.threading_event.is_set()

    def accept(self):
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(self.hostname)
        self.sock.listen(self.MAX_CLIENTS)  # listen for incoming connections
        self.sock.settimeout(self.TIMEOUT)
        while self.running:
            try:
                conn, hostname = self.sock.accept()
                conn.settimeout(self.TIMEOUT)
                t = threading.Thread(target=self.recv, args=(conn,))
                self.threads_conn[conn] = t
                t.start()

            # exception handling while communicating
            except socket.timeout:
                # print("socket accept timeout", file=sys.stderr)
                continue
        self.sock.close()

    def recv(self, conn):
        keep_running = True
        while self.running and keep_running:
            try:
                recv_len_bytes = conn.recv(self.MSGLEN_NBYTES)
                if recv_len_bytes:
                    command, args, kwargs = common.recv_and_unpack(conn, recv_len_bytes)
                    method = getattr(self.root, command)
                    if callable(method):
                        ret = method(*args, **kwargs)
                    else:   # object not callable, accessing variable
                        ret = method
                    common.pack_and_send(conn, ret)
                else:
                    # client disconnected
                    keep_running = False
            except (socket.timeout, ssl.SSLError):
                continue
        conn.close()
        self.threads_conn.pop(conn)
