import ssl
import socket
import threading

import common
from PyQt5.QtCore import QObject, QThread, pyqtSignal, pyqtSlot, QCoreApplication
from functools import partial
import traceback
import select
from collections import defaultdict


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
        self.buffers = defaultdict(list)
        # self.sig_new_connection.connect(self.slot_new_connection)
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
                # Use select to check if a new connection is available
                readable, _, _ = select.select([self.sock], [], [], self.TIMEOUT)

                if self.sock in readable:
                    conn, hostname = self.sock.accept()
                    conn.settimeout(self.TIMEOUT)
                    # new connection
                    t_exec = QThread(self)
                    t_exec.run = partial(self.recv, conn)
                    self.threads_exec[conn] = t_exec
                    # t_exec.finished.connect(partial(self.slot_stop_connection, conn))   # stops both exec and response threads
                    t_exec.start()

                    # self.sig_new_connection.emit(conn)

            except (socket.error, ssl.SSLError):
                continue  # Ignore errors and keep running

        self.sock.shutdown(socket.SHUT_RDWR)
        self.sock.close()

    # @pyqtSlot(socket.socket)
    # def slot_new_connection(self, conn):
    #     t_exec = QThread(self)
    #     t_exec.run = partial(self.recv, conn)
    #     self.threads_exec[conn] = t_exec
    #     # t_exec.finished.connect(partial(self.slot_stop_connection, conn))   # stops both exec and response threads
    #     t_exec.start()

    def recv(self, conn):
        while self.running:
            try:
                inputready, _, _ = select.select([conn], [], [], self.TIMEOUT)

                if conn in inputready:
                    recv_len_bytes = conn.recv(self.MSGLEN_NBYTES)

                    if recv_len_bytes:
                        command, args, kwargs = common.recv_and_unpack(conn, recv_len_bytes)
                        self.sig_exec.emit(conn, command, args, kwargs)
                    else:
                        # Client disconnected gracefully
                        print("Client disconnected")
                        break  # Exit loop to handle cleanup

            except (socket.timeout, ssl.SSLError):
                continue  # Ignore and retry

            except socket.error:
                print("SOCKET ERROR")
                print(traceback.format_exc())
                break  # Exit loop to handle cleanup

        # stop connection
        try:
            conn.shutdown(socket.SHUT_RDWR)
            conn.close()
        except Exception:
            pass  # Avoid exceptions if conn is already closed

        self.threads_exec.pop(conn, None)  # Prevent KeyError
        self.buffers.pop(conn, None)  # Prevent KeyError

    def event(self, event):
        if isinstance(event, common.PutToBufferEvent):     # put object to buffer
            conn = event.conn
            obj = event.obj
            print "sock host put to buffer event", event, obj, conn
            self.buffers[conn].append(obj)
            return True
        elif isinstance(event, common.EndBufferEvent):     # buffer end, send buffer to client
            conn = event.conn
            obj = self.buffers[conn][:]
            print "sock host end buffer event", event, obj, conn
            common.pack_and_send(conn, obj)
            del self.buffers[conn][:]
            return True
        else:
            return super(QSockHostQEventPoster, self).event(event)

    @pyqtSlot(socket.socket, str, tuple, dict)
    def slot_exec(self, conn, command, args, kwargs):    # exec in main thread
        try:
            method = getattr(self.root, command)
            if callable(method):
                ret = method(*args, **kwargs)   # callable method, administrative_xls_path(), etc.
            else:  # object not callable, accessing variable
                ret = method
            common.pack_and_send(conn, ret)
        except AttributeError:
            common.pack_and_send(conn, "unknown command")
