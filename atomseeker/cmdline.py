# -*- coding: utf-8 -*-

from optparse import OptionParser
import os
import sys

import atomseeker.atom
from jinja2 import Environment, FileSystemLoader

def main():
    "main function for command line tool"

    # parse options
    parser = OptionParser(usage = "usage: %prog [options] [input file]")

    # define options
    parser.add_option("--html", action = 'store_true', dest = 'html',
                      help = "output html format")

    (options, args) = parser.parse_args()

    # input file or stdin
    with open(args[0], 'rb') if len(args) > 0 else sys.stdin as i_f:

        if (options.html):
            result = atomseeker.atom.parse_atoms(i_f)
            dirname = os.path.normpath(os.path.dirname(__file__))
            env = Environment(loader = FileSystemLoader(os.path.join(dirname, "templates/"), encoding = 'utf8'))
            tpl = env.get_template("atom_top.tpl.html")
            html = tpl.render({'result': result, })
            sys.stdout.buffer.write(html.encode('utf-8'))
        else:
            atomseeker.atom.print_atoms(atomseeker.atom.parse_atoms(i_f))
