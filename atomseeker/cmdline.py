# -*- coding: utf-8 -*-

import argparse
import os
import sys

import atomseeker.atom
from jinja2 import Environment, FileSystemLoader


def main():
    """main function for command line tool"""

    # parse options
    parser = argparse.ArgumentParser()

    # define options
    parser.add_argument('file',
                        action='store',
                        type=argparse.FileType('rb'),
                        default=None,
                        nargs='?',
                        help='filename to be parsed (stdin will be used if omitted)')
    parser.add_argument('-H', '--html',
                        action='store_true',
                        dest='html',
                        help="output html format")

    args = parser.parse_args()

    # input file or stdin
    i_f = args.file if args.file else sys.stdin

    if args.html:
        result = atomseeker.atom.parse_atoms(i_f)
        dirname = os.path.normpath(os.path.dirname(__file__))
        env = Environment(loader=FileSystemLoader(
            os.path.join(dirname, "templates/"),
            encoding='utf8'
        ))
        tpl = env.get_template("atom_top.tpl.html")
        html = tpl.render({'result': result, })
        sys.stdout.buffer.write(html.encode('utf-8'))
    else:
        atomseeker.atom.print_atoms(atomseeker.atom.parse_atoms(i_f))
