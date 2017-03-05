# -*- coding: utf-8 -*-

import struct

def read_num(stream, num = 4):
    "return a number by 'num'-byte from 'stream'"

    data = stream.read(num)

    ret = 0
    for i in struct.unpack("B" * len(data), data)[0:num]:
        ret <<= 8
        ret += i

    return ret


def read_str(stream, num = 4):
    "return a string by 'num'-byte from 'stream'"

    data = read_num(stream, num)

    ret = ''

    for i in range(num):
        ret = ("%c" % (data & 0xff)) + ret
        data >>= 8

    return ret
