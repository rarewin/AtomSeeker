#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import struct

def read_num(stream, num = 4):
    "Return a number by consuming 'num' bytes from the current position of 'stream'."

    data = stream.read(num)

    ret = 0
    for i in struct.unpack("b" * len(data), data)[0:num]:
        ret <<= 8
        ret += i

    return ret

def read_str(stream, num = 4):

    data = read_num(stream, num)

    ret = ''

    for i in range(num):
        ret = ("%c" % (data & 0xff)) + ret
        data >>= 8

    return ret

class Atom:

    def __init__(self, stream):

        self.size = read_num(stream)
        self.type = read_str(stream)

        print(self.size)
        print(self.type)

        # self.type = type_to_str(stream)
