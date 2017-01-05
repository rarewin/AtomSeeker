#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import struct
import sys
import os

ATOMS_WITH_ONLY_CHILDREN = ['trak', 'edts', 'mdia', 'minf', 'stbl']

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


def parse_atoms(stream):
    "return Atom(s) from 'stream' until stream finish"

    ret = []

    while True:
        try:
            atom = parse_atom(stream)
            ret.append(atom)
        except ValueError:
            break

    return ret

def parse_atom(stream):
    "return Atom from 'stream'"

    t = stream.tell()

    _size = read_num(stream)
    _type = read_str(stream)

    #print("%s: %08x" % (_type, t))

    try:
        return eval("%s(stream, _size, _type)" % (_type))
    except NameError:

        if _type in ATOMS_WITH_ONLY_CHILDREN:
            return atom_with_only_children(stream, _size, _type)

        a = Atom(stream, _size, _type)
        stream.seek(_size - 8, os.SEEK_CUR)
        return a

def print_atoms(atoms, level = 0):
    "print atoms"

    for a in atoms:

        print("%s%s: %08x %08x" % (" " * level, a.type, a.size, a.tell))

        if hasattr(a, 'children'):
            print_atoms(a.children, level + 1)


class Atom:
    "basic atom class"

    def __init__(self, stream, size, type):

        self.size = size
        self.type = type
        self.tell = stream.tell() - 8

        try:
            self.with_version
        except AttributeError:
            self.with_version = False

        if (self.with_version):
            self.version = read_num(stream, 1)
            self.flags   = read_num(stream, 3)

    def parse_children(self, stream):

        cur_pos = self.tell

        _children = []

        while stream.tell() < cur_pos + self.size:
            child = parse_atom(stream)
            _children.append(child)

        setattr(self, 'children', _children)

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

        if self.size == 1:
            setattr(self, 'ExtendedSize', read_num(stream, 8))

        self.parse_children(stream)

class mvhd(Atom):
    "mvhd-atom class"

    def __init__(self, stream, size, type):

        self.with_version = True

        super().__init__(stream, size, type)

        setattr(self, 'Creation_time', read_num(stream))
        setattr(self, 'Modification_time', read_num(stream))
        setattr(self, 'Time_scale', read_num(stream))
        setattr(self, 'Duration', read_num(stream))
        setattr(self, 'Preferred_rate', read_num(stream))
        setattr(self, 'Preferred_volume', read_num(stream, 2))
        setattr(self, 'Reserved', read_num(stream, 10))

        setattr(self, 'Matrix_structure', [read_num(stream) for x in range(9)])

        setattr(self, 'Preview_time', read_num(stream))
        setattr(self, 'Preview_duration', read_num(stream))
        setattr(self, 'Poster_time', read_num(stream))
        setattr(self, 'Selection_time', read_num(stream))
        setattr(self, 'Selection_duration', read_num(stream))
        setattr(self, 'Current_time', read_num(stream))
        setattr(self, 'Next_track_ID', read_num(stream))

class tkhd(Atom):
    "tkhd-atom class"

    def __init__(self, stream, size, type):

        self.with_version = True

        super().__init__(stream, size, type)

        setattr(self, 'Creation_time', read_num(stream))
        setattr(self, 'Modification_time', read_num(stream))
        setattr(self, 'Track_ID', read_num(stream))
        setattr(self, 'Reserved', read_num(stream))
        setattr(self, 'Duration', read_num(stream))
        setattr(self, 'Reserved2', read_num(stream, 8))
        setattr(self, 'Layer', read_num(stream, 2))
        setattr(self, 'Alternate_group', read_num(stream, 2))
        setattr(self, 'Volume', read_num(stream, 2))
        setattr(self, 'Reserved3', read_num(stream, 2))

        setattr(self, 'Matrix_structure', [read_num(stream) for x in range(9)])

        setattr(self, 'Track_width', read_num(stream))
        setattr(self, 'Track_height', read_num(stream))

class mdhd(Atom):
    "mdhd-atom class"

    def __init__(self, stream, size, type):

        self.with_version = True

        super().__init__(stream, size, type)

        setattr(self, 'Creation_time', read_num(stream))
        setattr(self, 'Modification_time', read_num(stream))
        setattr(self, 'Time_scale', read_num(stream))
        setattr(self, 'Duration', read_num(stream))
        setattr(self, 'Language', read_str(stream, 2))
        setattr(self, 'Quality', read_str(stream, 2))

class atom_with_only_children(Atom,):

    def __init__(self, stream, size, type):

        super().__init__(stream, size, type)
        self.parse_children(stream)
