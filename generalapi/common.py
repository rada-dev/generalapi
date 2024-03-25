import struct


def int_from_bytes(b):
    return struct.unpack('<I', b)[0]


def int_to_bytes(n):
    return struct.pack('<I', n)


if __name__ == '__main__':
    a = 100
    print int_to_bytes(a), len(int_to_bytes(a))
    print int_from_bytes(int_to_bytes(a))