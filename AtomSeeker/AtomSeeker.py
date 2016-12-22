#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from optparse import OptionParser
import sys

import Atom

def main():

    # parse options
    parser = OptionParser()
    (options, args) = parser.parse_args()

    # input file or stdin
    with open(args[0], 'rb') if len(args) > 0 else sys.stdin as i_f:

        Atom.Atom(i_f)


if __name__ == '__main__':

    main()
