import Queue as queue
import ssl
import socket
import common
from PyQt5.QtCore import QObject, QThread, pyqtSignal, pyqtSlot, QEvent
from functools import partial
from multiprocessing import Queue
import traceback


class PutToBufferEvent(QEvent):
    EVENT_TYPE = QEvent.Type(QEvent.registerEventType())

    def __init__(self, obj):
        QEvent.__init__(self, PutToBufferEvent.EVENT_TYPE)  # Explicit QEvent constructor
        self.obj = obj


class EndBufferEvent(QEvent):
    EVENT_TYPE = QEvent.Type(QEvent.registerEventType())

    def __init__(self):
        QEvent.__init__(self, EndBufferEvent.EVENT_TYPE)  # Explicit QEvent constructor


class QSockHostQEventPoster(QObject):

    MAX_CLIENTS = 10
    TIMEOUT = 0.5

    MSGLEN_NBYTES = 4

    sig_new_connection = pyqtSignal(socket.socket)
    sig_exec = pyqtSignal(socket.socket, str, tuple, dict)

    def __init__(self, parent, sock, hostname, root, threading_event):
        super(QSockHostQEventPoster, self).__init__(parent)
        self.sock = sock
        self.hostname = hostname
        self.root = root
        self.threading_event = threading_event
        self.thread_accept = QThread(self)
        self.thread_accept.run = self.accept
        self.threads_exec = {}
        self.buffers = list()
        self.sig_new_connection.connect(self.slot_new_connection)
        self.sig_exec.connect(self.slot_exec)

    def start(self):
        self.threading_event.set()
        self.thread_accept.start()

    def stop(self):
        self.threading_event.clear()
        self.thread_accept.join()
        for t in self.threads_exec.values():
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
            except (socket.timeout, socket.error, ssl.SSLError):
                # print("socket accept timeout", file=sys.stderr)
                continue
        # self.sock.close()

    @pyqtSlot(socket.socket)
    def slot_new_connection(self, conn):
        t_exec = QThread(self)
        t_exec.run = partial(self.recv, conn)
        self.threads_exec[conn] = t_exec
        t_exec.finished.connect(partial(self.slot_stop_connection, conn))   # stops both exec and response threads
        t_exec.start()

    @pyqtSlot(socket.socket)
    def slot_stop_connection(self, conn):
        conn.close()
        self.threads_exec.pop(conn)

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
                print "SOCKET ERROR"
                print traceback.format_exc()
                # client disconnected (forcibly)
                keep_running = False

    def event(self, event):
        if event.type() == PutToBufferEvent.EVENT_TYPE:     # put object to buffer
            obj = event.obj
            conn = event.conn
            self.buffers[conn].append(obj)
            return True
        elif event.type() == EndBufferEvent.EVENT_TYPE:     # buffer end, send buffer to client
            obj = self.buffer[:]
            conn = event.conn
            common.pack_and_send(conn, obj)
            del self.buffer[:]
            return True
        else:
            return super(QSockHostQEventPoster, self).event(event)

    @pyqtSlot(socket.socket, str, tuple, dict)
    def slot_exec(self, conn, command, args, kwargs):    # exec in main thread
        method = getattr(self.root, command)
        if callable(method):
            ret = method(*args, **kwargs)   # callable method, administrative_xls_path(), etc.
        else:  # object not callable, accessing variable
            ret = method
        common.pack_and_send(conn, ret)
