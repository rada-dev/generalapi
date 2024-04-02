import struct
try:
    import cPickle as pickle
except ImportError:
    import pickle
import configparser
import io


MSGDTYPE_PICKLE = chr(0)
MSGDTYPE_CONFIGPARSER = chr(1)

MSGLEN_NBYTES = 4


def pack(data):
    try:
        return MSGDTYPE_PICKLE, pickle.dumps(data)
    except TypeError:   # cannot pickle
        if isinstance(data, configparser.ConfigParser):
            b = io.StringIO()
            data.write(b)
            return MSGDTYPE_CONFIGPARSER, b.getvalue()
        raise AssertionError("unsupported object to pickle")


def pack_and_send(conn, data):
    dtype_bytes, msg_bytes = pack(data)
    len_bytes = int_to_bytes(len(msg_bytes))
    conn.send(len_bytes)
    conn.send(dtype_bytes)
    conn.send(msg_bytes)


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