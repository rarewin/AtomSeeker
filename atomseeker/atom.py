# -*- coding: utf-8 -*-

import sys
import os
from collections import OrderedDict

from atomseeker import elements
from atomseeker.func import *

ATOMS_WITH_ONLY_CHILDREN = ['trak', 'edts', 'mdia', 'minf', 'stbl', 'dinf']

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

def parse_atom(stream, parent = None):
    "return Atom from 'stream'"

    t = stream.tell()

    _size = read_num(stream)
    _type = read_str(stream)

    try:
        return eval("%s(stream, _size, _type, parent)" % (_type))
    except NameError:

        if _type in ATOMS_WITH_ONLY_CHILDREN:
            return atom_with_only_children(stream, _size, _type, parent)

        a = Atom(stream, _size, _type, parent)
        stream.seek(_size - 8, os.SEEK_CUR)
        return a

def print_atoms(atoms, level = 0):
    "print atoms"

    for a in atoms:

        print("%s%s: %08x %08x" % (" " * level, a.type, a.size, a.tell))

        if hasattr(a, 'version'):
            print(" %s| '%s' = %s" % (" " * level, 'Version', a.version))
            print(" %s| '%s' = %s" % (" " * level, 'Flags', a.flags))

        for k, v in a.elements.items():
            print(" %s| '%s' = %s" % (" " * level, k, v))

        # print if 'a' has the attribute 'children'
        if hasattr(a, 'children'):
            print_atoms(a.children, level + 1)

class Atom:
    "basic atom class"

    def __init__(self, stream, size, type, parent):

        self.size = size
        self.type = type
        self.tell = stream.tell() - 8
        self.parent = parent

        try:
            self.with_version
        except AttributeError:
            self.with_version = False

        if self.with_version:
            self.version = read_num(stream, 1)
            self.flags   = read_num(stream, 3)

        self.elements = OrderedDict()

    def parse_children(self, stream):

        cur_pos = self.tell

        _children = []

        while stream.tell() < cur_pos + self.size:
            child = parse_atom(stream, self)
            _children.append(child)

        self.children = _children

class ftyp(Atom):
    "ftyp-atom class"

    def __init__(self, stream, size, type, parent):

        super().__init__(stream, size, type, parent)

        self.elements['Major_Brand']   = read_str(stream, 4)
        self.elements['Minor_Version'] = read_num(stream, 4)

        tmp = []

        for i in range((self.size - 16) // 4):
            tmp.append(read_str(stream, 4))

        self.elements['Compatible_Brands'] = tmp

class moov(Atom):
    "moov-atom class"

    def __init__(self, stream, size, type, parent):

        super().__init__(stream, size, type, parent)

        if self.size == 1:
            self.elements['ExtendedSize'] = read_num(stream, 8)

        self.parse_children(stream)

class mvhd(Atom):
    "mvhd-atom class"

    def __init__(self, stream, size, type, parent):

        self.with_version = True

        super().__init__(stream, size, type, parent)

        self.elements['Creation_time'] = elements.AtomDate(read_num(stream))
        self.elements['Modification_time'] = elements.AtomDate(read_num(stream))
        self.elements['Time_scale'] = read_num(stream)
        self.elements['Duration'] = read_num(stream)
        self.elements['Preferred_rate'] = read_num(stream)
        self.elements['Preferred_volume'] = read_num(stream,2)
        self.elements['Reserved'] = read_num(stream, 10)
        self.elements['Matrix_structure'] = elements.AtomMatrix([read_num(stream) for i in range(9)])
        self.elements['Preview_time'] = elements.AtomDate(read_num(stream))
        self.elements['Preview_duration'] = read_num(stream)
        self.elements['Poster_time'] = elements.AtomDate(read_num(stream))
        self.elements['Selection_time'] = elements.AtomDate(read_num(stream))
        self.elements['Selection_duration'] = read_num(stream)
        self.elements['Current_time'] = elements.AtomDate(read_num(stream))
        self.elements['Next_track_ID'] = read_num(stream)

class tkhd(Atom):
    "tkhd-atom class"

    def __init__(self, stream, size, type, parent):

        self.with_version = True

        super().__init__(stream, size, type, parent)

        self.elements['Creation_time'] = elements.AtomDate(read_num(stream))
        self.elements['Modification_time'] = elements.AtomDate(read_num(stream))
        self.elements['Track_ID'] = read_num(stream)
        self.elements['Reserved'] = read_num(stream)
        self.elements['Duration'] = read_num(stream)
        self.elements['Reserved2'] = read_num(stream, 8)
        self.elements['Layer'] = read_num(stream, 2)
        self.elements['Alternate_group'] = read_num(stream, 2)
        self.elements['Volume'] = read_num(stream, 2)
        self.elements['Reserved3'] = read_num(stream, 2)
        self.elements['Matrix_structure'] = elements.AtomMatrix([read_num(stream) for i in range(9)])
        self.elements['Track_width'] = read_num(stream)
        self.elements['Track_height'] = read_num(stream)

class mdhd(Atom):
    "mdhd-atom class"

    def __init__(self, stream, size, type, parent):

        self.with_version = True

        super().__init__(stream, size, type, parent)

        self.elements['Creation_time'] = elements.AtomDate(read_num(stream))
        self.elements['Modification_time'] = elements.AtomDate(read_num(stream))
        self.elements['Time_scale'] = read_num(stream)
        self.elements['Duration'] = read_num(stream)
        self.elements['Language'] = read_str(stream, 2)
        self.elements['Quality'] = read_str(stream, 2)

class elst(Atom):
    "elst-atom class"

    def __init__(self, stream, size, type, parent):

        self.with_version = True
        super().__init__(stream, size, type, parent)

        self.elements['Number_of_entries'] = read_num(stream)
        self.elements['Edit_list_table'] = [[read_num(stream) for y in range(3)] for x in range(self.elements['Number_of_entries'])]

class dref(Atom):
    "dref-atom class"

    def __init__(self, stream, size, type, parent):

        self.with_version = True
        super().__init__(stream, size, type, parent)

        self.elements['Number_of_entries'] = read_num(stream)
        self.parse_children(stream)

class vmhd(Atom):
    "vmhd-atom class"

    def __init__(self, stream, size, type, parent):

        self.with_version = True
        super().__init__(stream, size, type, parent)

        self.elements['Graphics_mode'] = read_num(stream, 2)
        self.elements['Opcolor'] = [read_num(stream, 2) for x in range(3)]

class stsd(Atom):
    "stsd-atom class"

    def __init__(self, stream, size, type, parent):

        self.with_version = True
        super().__init__(stream, size, type, parent)

        self.elements['Number_of_entries'] = read_num(stream)

        #stream.seek(self.size - 16, os.SEEK_CUR)

        self.parse_children(stream)

class mp4a(Atom):
    "mp4a sample descriptor atom"

    def __init__(self, stream, size, type, parent):

        super().__init__(stream, size, type, parent)

        self.elements['Reserved'] = read_num(stream, 6)
        self.elements['Data_reference_Index'] = read_num(stream, 2)
        self.elements['Version'] = read_num(stream, 2)

        # change parse according to stsd version.
        if self.elements['Version'] == 0:

            self.elements['Revision_level'] = read_num(stream, 2)
            self.elements['Vendor'] = read_num(stream)
            self.elements['Number_of_channels'] = read_num(stream, 2)
            self.elements['Sample_size'] = read_num(stream, 2)
            self.elements['Comparison_ID'] = read_num(stream, 2)
            self.elements['Packet_size'] = read_num(stream, 2)
            self.elements['Sample_rate'] = read_num(stream)

            self.parse_children(stream)

        else:
            stream.seek(self.size - 18, os.SEEK_CUR)

class esds(Atom):
    "esds sample descriptor atom"

    def __init__(self, stream, size, type, parent):

        super().__init__(stream, size, type, parent)

        self.elements['Version'] = read_num(stream)
        stream.seek(self.size - 12, os.SEEK_CUR)

class atom_with_only_children(Atom,):
    "atoms that have only children"

    def __init__(self, stream, size, type, parent):

        super().__init__(stream, size, type, parent)
        self.parse_children(stream)
