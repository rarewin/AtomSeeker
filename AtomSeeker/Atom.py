#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import struct
import sys
import os

def read_num(stream, num = 4):
    "return a number by consuming 'num' bytes from the current position of 'stream'."

    data = stream.read(num)

    ret = 0
    for i in struct.unpack("b" * len(data), data)[0:num]:
        ret <<= 8
        ret += i

    return ret

def read_str(stream, num = 4):
    "return a string by consuming 'numr' bytes from the current position of 'stream'."

    data = read_num(stream, num)

    ret = ''

    for i in range(num):
        ret = ("%c" % (data & 0xff)) + ret
        data >>= 8

    return ret

def parse_atom(stream):

    _size = read_num(stream)
    _type = read_str(stream)

    print(_type)

    try:
        return eval("%s(stream, _size, _type)" % (_type))
    except NameError:
        a = Atom(stream, _size, _type)
    #    stream.seek(_size - 8, os.SEEK_CUR)
        return a

class Atom:

    def __init__(self, stream, size, type):

        self.size = size
        self.type = type

class ftyp(Atom):
    "ftyp-atom class"

    def __init__(self, stream, size, type):

        super().__init__(stream, size, type)

        setattr(self, 'Major_Brand', read_str(stream, 4))
        setattr(self, 'Minor_Version', read_num(stream, 4))

        tmp = []

        for i in range((self.size - 16) // 4):
            tmp.append(read_str(stream, 4))

        setattr(self, 'Compatible_Brands', tmp)

class moov(Atom):
    "moov-atom class"

    def __init__(self, stream, size, type):

        super().__init__(stream, size, type)

        cur_pos = stream.tell() - 8		# type and size

        if self.size == 1:
            setattr(self, 'ExtendedSize', read_num(stream, 8))

        children = []

        while stream.tell() < cur_pos + self.size:
            child = parse_atom(stream)
            children.append(child)

        setattr(self, 'children', children)
