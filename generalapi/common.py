import numpy as np
import struct
try:
    import cPickle as pickle
except ImportError:
    import pickle
import configparser
import base64
import io


MSGDTYPE_PICKLE = chr(0)
MSGDTYPE_CONFIGPARSER = chr(1)
MSGDTYPE_NUMPY = chr(2)

MSGLEN_NBYTES = 4


def pack(data):
    # if isinstance(data, np.ndarray):
    #     return MSGDTYPE_NUMPY, numpy_arr_to_buff(data)
    if isinstance(data, configparser.ConfigParser):
        b = io.StringIO()
        data.write(b)
        return MSGDTYPE_CONFIGPARSER, b.getvalue()
    else:
        return MSGDTYPE_PICKLE, pickle.dumps(data)


def pack_and_send(conn, data):
    dtype_bytes, msg_bytes = pack(data)
    len_bytes = int_to_bytes(len(msg_bytes))
    conn.sendall(len_bytes+dtype_bytes+msg_bytes)
    # conn.sendall(dtype_bytes)
    # conn.sendall(msg_bytes)


def recv_and_unpack(conn, recv_len_bytes):
    recv_len = int_from_bytes(recv_len_bytes)  # receive packet
    dtype_bytes = conn.recv(1)
    pickled_msg = conn.recv(recv_len)
    return unpack(dtype_bytes, pickled_msg)


def unpack(dtype, msg):
    if dtype == MSGDTYPE_PICKLE:
        return pickle.loads(msg)
    elif dtype == MSGDTYPE_CONFIGPARSER:
        c = configparser.ConfigParser()
        c.read_string(msg.decode("utf-8"))
        return c
    # elif dtype == MSGDTYPE_NUMPY:
    #     return numpy_msg_to_arr(msg)
    else:
        raise AssertionError("unsupported message dtype")


def numpy_arr_to_buff(arr):
    buff = io.BytesIO()
    np.save(buff, arr)
    buff.seek(0)  # Reset buffer position to the beginning
    buff_data = buff.getvalue()
    return buff_data


def numpy_msg_to_arr(msg):
    buff = io.BytesIO()
    buff.write(msg)
    buff.seek(0)  # Reset buffer position to the beginning
    array = np.load(buff)
    return array


def int_from_bytes(b):
    return struct.unpack('<I', b)[0]


def int_to_bytes(n):
    return struct.pack('<I', n)


if __name__ == '__main__':
    # x = np.eye(50)
    # b = pickle.dumps(x)
    # print pickle.loads(b)

    # x_enc = msgpack.packb(x, default=m.encode)
    # x_rec = msgpack.unpackb(x_enc, object_hook=m.decode)

    a = 100
    print int_to_bytes(a), len(int_to_bytes(a))
    print int_from_bytes(int_to_bytes(a))