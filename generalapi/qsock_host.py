import ssl
import socket
import common
import cPickle as pickle
from PyQt5.QtCore import QObject, QThread, pyqtSignal, pyqtSlot
from functools import partial


class QSockHost(QObject):

    MAX_CLIENTS = 10
    TIMEOUT = 0.5

    MSGLEN_NBYTES = 4

    sig_new_connection = pyqtSignal(socket.socket)
    sig_exec = pyqtSignal(socket.socket, str, tuple, dict)

    def __init__(self, parent, sock, hostname, root, threading_event):
        super(QSockHost, self).__init__(parent)
        self.sock = sock
        self.hostname = hostname
        self.root = root
        self.main_thread = self.thread()
        self.threading_event = threading_event
        self.thread_accept = QThread(self)
        self.thread_accept.run = self.accept
        self.threads_conn = {}
        self.sig_new_connection.connect(self.slot_new_connection)
        self.sig_exec.connect(self.slot_exec)

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
                self.sig_new_connection.emit(conn)

            # exception handling while communicating
            except socket.timeout:
                # print("socket accept timeout", file=sys.stderr)
                continue
        self.sock.close()

    @pyqtSlot(socket.socket)
    def slot_new_connection(self, conn):
        t = QThread(self)
        t.run = partial(self.recv, conn)
        t.finished.connect(partial(self.slot_stop_connection, conn))
        self.threads_conn[conn] = t
        t.start()

    @pyqtSlot(socket.socket)
    def slot_stop_connection(self, conn):
        conn.close()
        self.threads_conn.pop(conn)

    def recv(self, conn):
        keep_running = True
        while self.running and keep_running:
            try:
                recv_len_bytes = conn.recv(self.MSGLEN_NBYTES)
                if recv_len_bytes:
                    recv_len = common.int_from_bytes(recv_len_bytes)  # receive packet
                    pickled_msg = conn.recv(recv_len)
                    command, args, kwargs = pickle.loads(pickled_msg)
                    self.sig_exec.emit(conn, command, args, kwargs)
                else:
                    # client disconnected
                    keep_running = False
            except (socket.timeout, ssl.SSLError):
                continue

    @pyqtSlot(socket.socket, str, tuple, dict)
    def slot_exec(self, conn, command, args, kwargs):    # exec in main thread
        method = getattr(self.root, command)
        if callable(method):
            ret = method(*args, **kwargs)
        else:  # object not callable, accessing variable
            ret = method
        pickled_ret = pickle.dumps(ret)
        ret_len_bytes = common.int_to_bytes(len(pickled_ret))
        conn.send(ret_len_bytes)
        conn.send(pickled_ret)
