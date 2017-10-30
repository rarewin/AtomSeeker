# -*- coding: utf-8 -*-

import struct
import os
from collections import OrderedDict

from atomseeker import elements

ATOMS_WITH_ONLY_CHILDREN = ['trak', 'edts', 'mdia', 'minf', 'stbl']


def read_num(stream, num=4):
    """return a number by 'num'-byte from 'stream'"""

    data = stream.read(num)

    ret = 0
    for i in struct.unpack("B" * len(data), data)[0:num]:
        ret <<= 8
        ret += i

    return ret


def read_str(stream, num=4):
    """return a string by 'num'-byte from 'stream'"""

    data = read_num(stream, num)

    ret = ''

    for i in range(num):
        ret = ("%c" % (data & 0xff)) + ret
        data >>= 8

    return ret


def parse_atoms(stream):
    """return Atom(s) from 'stream' until stream finish"""

    ret = []

    while True:
        try:
            atom = parse_atom(stream)
            ret.append(atom)
        except ValueError:
            break

    return ret


def parse_atom(stream):
    """return Atom from 'stream'"""

    t = stream.tell()

    _size = read_num(stream)
    _type = read_str(stream)

    # print("%s: %08x" % (_type, t))

    try:
        return eval("%s(stream, _size, _type)" % _type)
    except NameError:

        if _type in ATOMS_WITH_ONLY_CHILDREN:
            return AtomWithOnlyChildren(stream, _size, _type)

        a = Atom(stream, _size, _type)
        stream.seek(_size - 8, os.SEEK_CUR)
        return a


def print_atoms(atoms, level=0):
    """print atoms"""

    for a in atoms:

        print("%s%s: %08x %08x" % (" " * level, a.type, a.size, a.tell))

        for k, v in a.elements.items():
            print(" %s| '%s' = %s" % (" " * level, k, v))

        # print if 'a' has the attribute 'children'
        if hasattr(a, 'children'):
            print_atoms(a.children, level + 1)


class Atom:
    """basic atom class"""

    def __init__(self, stream, size, type):

        self.size = size
        self.type = type
        self.tell = stream.tell() - 8

        try:
            self.with_version
        except AttributeError:
            self.with_version = False

        if self.with_version:
            self.version = read_num(stream, 1)
            self.flags = read_num(stream, 3)

        self.elements = OrderedDict()

    def parse_children(self, stream):

        cur_pos = self.tell

        _children = []

        while stream.tell() < cur_pos + self.size:
            child = parse_atom(stream)
            _children.append(child)

        self.children = _children


class FTYP(Atom):
    """ftyp-atom class"""

    def __init__(self, stream, size, type):

        super().__init__(stream, size, type)

        self.elements['Major_Brand'] = read_str(stream, 4)
        self.elements['Minor_Version'] = read_num(stream, 4)

        tmp = []

        for i in range((self.size - 16) // 4):
            tmp.append(read_str(stream, 4))

        self.elements['Compatible_Brands'] = tmp


class MOOV(Atom):
    """moov-atom class"""

    def __init__(self, stream, size, type):

        super().__init__(stream, size, type)

        if self.size == 1:
            self.elements['ExtendedSize'] = read_num(stream, 8)

        self.parse_children(stream)


class MVHD(Atom):
    """mvhd-atom class"""

    def __init__(self, stream, size, type):

        self.with_version = True

        super().__init__(stream, size, type)

        self.elements['Creation_time'] = elements.AtomDate(read_num(stream))
        self.elements['Modification_time'] = (
            elements.AtomDate(read_num(stream)))
        self.elements['Time_scale'] = read_num(stream)
        self.elements['Duration'] = read_num(stream)
        self.elements['Preferred_rate'] = read_num(stream)
        self.elements['Preferred_volume'] = read_num(stream, 2)
        self.elements['Reserved'] = read_num(stream, 10)
        self.elements['Matrix_structure'] = (
            elements.AtomMatrix([read_num(stream) for _ in range(9)]))
        self.elements['Preview_time'] = elements.AtomDate(read_num(stream))
        self.elements['Preview_duration'] = read_num(stream)
        self.elements['Poster_time'] = elements.AtomDate(read_num(stream))
        self.elements['Selection_time'] = elements.AtomDate(read_num(stream))
        self.elements['Selection_duration'] = read_num(stream)
        self.elements['Current_time'] = elements.AtomDate(read_num(stream))
        self.elements['Next_track_ID'] = read_num(stream)


class TKHD(Atom):
    """tkhd-atom class"""

    def __init__(self, stream, size, type):

        self.with_version = True

        super().__init__(stream, size, type)

        self.elements['Creation_time'] = elements.AtomDate(read_num(stream))
        self.elements['Modification_time'] = (
            elements.AtomDate(read_num(stream)))
        self.elements['Track_ID'] = read_num(stream)
        self.elements['Reserved'] = read_num(stream)
        self.elements['Duration'] = read_num(stream)
        self.elements['Reserved2'] = read_num(stream, 8)
        self.elements['Layer'] = read_num(stream, 2)
        self.elements['Alternate_group'] = read_num(stream, 2)
        self.elements['Volume'] = read_num(stream, 2)
        self.elements['Reserved3'] = read_num(stream, 2)
        self.elements['Matrix_structure'] = (
            elements.AtomMatrix([read_num(stream) for _ in range(9)]))
        self.elements['Track_width'] = read_num(stream)
        self.elements['Track_height'] = read_num(stream)


class MDHD(Atom):
    """mdhd-atom class"""

    def __init__(self, stream, size, type):

        self.with_version = True

        super().__init__(stream, size, type)

        self.elements['Creation_time'] = elements.AtomDate(read_num(stream))
        self.elements['Modification_time'] = (
            elements.AtomDate(read_num(stream)))
        self.elements['Time_scale'] = read_num(stream)
        self.elements['Duration'] = read_num(stream)
        self.elements['Language'] = read_str(stream, 2)
        self.elements['Quality'] = read_str(stream, 2)


class ELST(Atom):
    """elst-atom class"""

    def __init__(self, stream, size, type):

        self.with_version = True
        super().__init__(stream, size, type)

        self.elements['Number_of_entries'] = read_num(stream)
        self.elements['Edit_list_table'] = [
            [read_num(stream) for _ in range(3)]
            for _ in range(self.elements['Number_of_entries'])
        ]


class AtomWithOnlyChildren(Atom, ):

    def __init__(self, stream, size, type):

        super().__init__(stream, size, type)
        self.parse_children(stream)
