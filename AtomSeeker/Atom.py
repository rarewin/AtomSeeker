#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import struct
import sys

atom_types = ['ftyp']

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

class Atom:

    def __init__(self, stream):

        self.size = read_num(stream)
        self.type = read_str(stream)

        if self.type in atom_types:
            eval("%s(self, stream)" % (self.type))
        else:
            print("Unknown type...stop: %s" % (self.type))
            sys.exit()

def ftyp(self, stream):
    "ftyp-atom parser"

    setattr(self, 'Major_Brand', read_str(stream, 4))
    setattr(self, 'Minor_Version', read_num(stream, 4))

    tmp = []

    for i in range((self.size - 16) // 4):
        tmp.append(read_str(stream, 4))

    setattr(self, 'Compatible_Brands', tmp)

def moov(self, stream):

    if self.size == 1:
        setattr(self, 'ExtendedSize', read_num(stream, 8))

    children = []

