import Queue as queue
import ssl
import socket
import common
from PyQt5.QtCore import QObject, QThread, pyqtSignal, pyqtSlot
from functools import partial
from multiprocessing import Queue


class QSockHost(QObject):

    MAX_CLIENTS = 10
    TIMEOUT = 0.5

    MSGLEN_NBYTES = 4

    sig_new_connection = pyqtSignal(socket.socket)
    sig_exec = pyqtSignal(socket.socket, str, tuple, dict)
    sig_exec_response = pyqtSignal(socket.socket, object)

    def __init__(self, parent, sock, hostname, root, threading_event):
        super(QSockHost, self).__init__(parent)
        self.sock = sock
        self.hostname = hostname
        self.root = root
        self.main_thread = self.thread()
        self.threading_event = threading_event
        self.thread_accept = QThread(self)
        self.thread_accept.run = self.accept
        self.threads_exec = {}
        self.threads_response = {}
        self.q_response = Queue()
        self.sig_new_connection.connect(self.slot_new_connection)
        self.sig_exec.connect(self.slot_exec)
        self.sig_exec_response.connect(self.slot_exec_response)

    def start(self):
        self.threading_event.set()
        self.thread_accept.start()

    def stop(self):
        self.threading_event.clear()
        self.thread_accept.join()
        for t in self.threads_exec.values():
            t.join()
        for t in self.threads_response.values():
            t.join()

    def clients(self):
        return self.threads_exec.keys()

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
        t_exec = QThread(self)
        t_exec.run = partial(self.recv, conn)
        self.threads_exec[conn] = t_exec
        t_response = QThread(self)
        t_response.run = partial(self.respond_images_from_queue, conn)
        self.threads_response[conn] = t_response
        t_exec.finished.connect(partial(self.slot_stop_connection, conn))   # stops both exec and response threads
        t_exec.start()
        t_response.start()

    @pyqtSlot(socket.socket)
    def slot_stop_connection(self, conn):
        conn.close()
        self.threads_exec.pop(conn)
        self.threads_response.pop(conn)

    def recv(self, conn):
        keep_running = True
        while self.running and keep_running:
            try:
                recv_len_bytes = conn.recv(self.MSGLEN_NBYTES)
                if recv_len_bytes:
                    command, args, kwargs = common.recv_and_unpack(conn, recv_len_bytes)
                    self.sig_exec.emit(conn, command, args, kwargs)
                else:
                    # client disconnected
                    keep_running = False
            except (socket.timeout, ssl.SSLError):
                continue
            except socket.error:
                # client disconnected (forcibly)
                keep_running = False

    def respond_images_from_queue(self, conn):
        keep_running = True
        while self.running and keep_running:
            try:
                resp = self.q_response.get()
                data = []
                while resp != "end":
                    data.append(resp)
                    resp = self.q_response.get()
                self.sig_exec_response.emit(conn, data)
            except (socket.timeout, ssl.SSLError):
                continue

    @pyqtSlot(socket.socket, str, tuple, dict)
    def slot_exec(self, conn, command, args, kwargs):    # exec in main thread
        method = getattr(self.root, command)
        if callable(method):
            ret = method(*args, **kwargs)
        else:  # object not callable, accessing variable
            ret = method
        # if not respond_from_queue:  # respond either here directly or by waiting for queue data
        self.sig_exec_response.emit(conn, ret)

    @pyqtSlot(socket.socket, object)
    def slot_exec_response(self, conn, ret):
        common.pack_and_send(conn, ret)

    def clear_queue(self):
        while True:
            try:
                self.q_response.get_nowait()
            except queue.Empty:
                return

