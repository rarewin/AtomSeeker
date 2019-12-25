# -*- coding: utf-8 -*-

import struct
import os
from collections import OrderedDict

from atomseeker import elements

ATOMS_WITH_ONLY_CHILDREN = ("trak", "edts", "mdia", "minf", "stbl")
ATOMS_WITH_VERSION = ("mvhd", "tkhd", "mdhd", "elst")


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

    ret = ""

    for i in range(num):
        ret = ("%c" % (data & 0xFF)) + ret
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

    offset = stream.tell()
    size = read_num(stream)
    type = read_str(stream)

    # print("%s: %08x" % (_type, t))

    if size != 1:
        stream.seek(-8, os.SEEK_CUR)
    else:
        size = read_num(stream, 8)  # extended size
        stream.seek(-16, os.SEEK_CUR)

    try:
        return eval("{}Atom(stream, size, type, offset)".format(type.capitalize()))
    except NameError:

        if type in ATOMS_WITH_ONLY_CHILDREN:
            return AtomWithOnlyChildren(stream, size, type, offset)

        a = Atom(stream, size, type, offset)

        stream.seek(offset + size, os.SEEK_SET)

        return a


def print_atoms(atoms, level=0):
    """print atoms"""

    for a in atoms:

        print("%s%s: %08x %08x" % (" " * level, a.type, a.size, a.offset))

        for k, v in a.elements.items():
            print(" %s| '%s' = %s" % (" " * level, k, v))

        # print if 'a' has the attribute 'children'
        if hasattr(a, "children"):
            print_atoms(a.children, level + 1)


class Atom:
    """basic atom class"""

    __slots__ = ("size", "esize", "type", "offset", "version", "flags", "elements")

    def __init__(self, stream, size, type, offset):

        self.size = size
        self.type = type
        self.offset = offset

        stream.seek(offset, os.SEEK_SET)
        r_size = read_num(stream, 4)
        r_type = read_str(stream, 4)

        # extended size
        if r_size == 1:
            r_size = read_num(stream, 8)

        # assertion
        if r_size != size or r_type != type:
            raise ValueError("failed to parse")

        if self.type in ATOMS_WITH_VERSION:
            self.version = read_num(stream, 1)
            self.flags = read_num(stream, 3)
        else:
            self.version = None
            self.flags = None

        self.elements = OrderedDict()

    def parse_children(self, stream):

        cur_pos = self.offset

        _children = []

        while stream.tell() < cur_pos + self.size:
            child = parse_atom(stream)
            _children.append(child)

        self.children = _children


class FtypAtom(Atom):
    """ftyp-atom class"""

    def __init__(self, stream, size, type, offset):

        super().__init__(stream, size, type, offset)

        self.elements["Major_Brand"] = read_str(stream, 4)
        self.elements["Minor_Version"] = read_num(stream, 4)

        tmp = []

        for i in range((self.size - 16) // 4):
            tmp.append(read_str(stream, 4))

        self.elements["Compatible_Brands"] = tmp


class MoovAtom(Atom):
    """moov-atom class"""

    def __init__(self, stream, size, type, offset):

        super().__init__(stream, size, type, offset)

        self.parse_children(stream)


class MvhdAtom(Atom):
    """mvhd-atom class"""

    def __init__(self, stream, size, type, offset):

        super().__init__(stream, size, type, offset)

        self.elements["Creation_time"] = elements.AtomDate(read_num(stream))
        self.elements["Modification_time"] = elements.AtomDate(read_num(stream))
        self.elements["Time_scale"] = read_num(stream)
        self.elements["Duration"] = read_num(stream)
        self.elements["Preferred_rate"] = read_num(stream)
        self.elements["Preferred_volume"] = read_num(stream, 2)
        self.elements["Reserved"] = read_num(stream, 10)
        self.elements["Matrix_structure"] = elements.AtomMatrix(
            [read_num(stream) for _ in range(9)]
        )
        self.elements["Preview_time"] = elements.AtomDate(read_num(stream))
        self.elements["Preview_duration"] = read_num(stream)
        self.elements["Poster_time"] = elements.AtomDate(read_num(stream))
        self.elements["Selection_time"] = elements.AtomDate(read_num(stream))
        self.elements["Selection_duration"] = read_num(stream)
        self.elements["Current_time"] = elements.AtomDate(read_num(stream))
        self.elements["Next_track_ID"] = read_num(stream)


class TkhdAtom(Atom):
    """tkhd-atom class"""

    def __init__(self, stream, size, type, offset):

        super().__init__(stream, size, type, offset)

        self.elements["Creation_time"] = elements.AtomDate(read_num(stream))
        self.elements["Modification_time"] = elements.AtomDate(read_num(stream))
        self.elements["Track_ID"] = read_num(stream)
        self.elements["Reserved"] = read_num(stream)
        self.elements["Duration"] = read_num(stream)
        self.elements["Reserved2"] = read_num(stream, 8)
        self.elements["Layer"] = read_num(stream, 2)
        self.elements["Alternate_group"] = read_num(stream, 2)
        self.elements["Volume"] = read_num(stream, 2)
        self.elements["Reserved3"] = read_num(stream, 2)
        self.elements["Matrix_structure"] = elements.AtomMatrix(
            [read_num(stream) for _ in range(9)]
        )
        self.elements["Track_width"] = read_num(stream)
        self.elements["Track_height"] = read_num(stream)


class MdhdAtom(Atom):
    """mdhd-atom class"""

    def __init__(self, stream, size, type, offset):

        super().__init__(stream, size, type, offset)

        self.elements["Creation_time"] = elements.AtomDate(read_num(stream))
        self.elements["Modification_time"] = elements.AtomDate(read_num(stream))
        self.elements["Time_scale"] = read_num(stream)
        self.elements["Duration"] = read_num(stream)
        self.elements["Language"] = elements.AtomLanguageCodeValue(read_num(stream, 2))
        self.elements["Quality"] = read_num(stream, 2)


class ElstAtom(Atom):
    """elst-atom class"""

    def __init__(self, stream, size, type, offset):

        super().__init__(stream, size, type, offset)

        self.elements["Number_of_entries"] = read_num(stream)
        self.elements["Edit_list_table"] = [
            [read_num(stream) for _ in range(3)]
            for _ in range(self.elements["Number_of_entries"])
        ]


class AtomWithOnlyChildren(Atom):
    def __init__(self, stream, size, type, offset):

        super().__init__(stream, size, type, offset)
        self.parse_children(stream)
