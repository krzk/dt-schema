#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause

import argparse
import glob
import os
import re

verbose = False

class DtsStyle():
    def __init__(self, filename):
        self.warnings = []
        self.__filename = filename
        self.__handlers = [
            (re.compile(r'^\s*(?P<label>[a-zA-Z0-9,_-]+:)?(?P<s1>\s*)(?P<nodename>[a-zA-Z0-9,_-]+)(@(?P<unitaddr>[0-9a-fA-FxX]+))?(?P<s2>\s*)\{(?P<s3>\s*)$'),
             self.handle_node),
            (re.compile(r'^(?P<s1>\s*)(?P<label>&[a-zA-Z0-9,_-]+)?(?P<s2>\s*)\{(?P<s3>\s*)$'),
             self.handle_node_extend),
            ]

    def check_node_name(self, line, ln, match):
        label = match.group('label')
        nodename = match.group('nodename')
        unitaddr = match.group('unitaddr')
        if label:
            if match.group('s1') != ' ':
                self.warnings.append(['Whitespace error', line, ln])
            if '-' in label:
                self.warnings.append(['Label: use underscores instead of hyphens', line, ln])
            if re.search('[A-Z]', label):
                self.warnings.append(['Label: only lowercase letters', line, ln])
        if match.group('s2') != ' ' or match.group('s3'):
            self.warnings.append(['Whitespace error', line, ln])
        if '_' in nodename:
            self.warnings.append(['Node name: use hyphens instead of underscores', line, ln])
        if re.search('[A-Z]', nodename):
            self.warnings.append(['Node name: only lowercase letters', line, ln])
        if unitaddr:
            if re.search('[A-F]', unitaddr):
                self.warnings.append(['Unit address: only lowercase hex', line, ln])
            if re.search('[xX]', unitaddr):
                self.warnings.append(['Unit address: avoid "0x"', line, ln])
            if re.search('^0+[1-9a-f][0-9a-f]*$', unitaddr):
                self.warnings.append(['Unit address: avoid leading "0"', line, ln])

    def check_label(self, line, ln, match):
        label = match.group('label')
        if match.group('s1') or match.group('s2') != ' ' or match.group('s3'):
            self.warnings.append(['Whitespace error', line, ln])
        if '-' in label:
            self.warnings.append(['Label: use underscores instead of hyphens', line, ln])
        if re.search('[A-Z]', label):
            self.warnings.append(['Label: only lowercase letters', line, ln])

    def handle_node(self, line, ln, match):
        self.check_node_name(line, ln, match)

    def handle_node_extend(self, line, ln, match):
        self.check_label(line, ln, match)

    def check_dts(self,):
        """Check the given DTS/DTSI/DTSO for style"""
        with open(self.__filename, 'r') as f:
            i = 1
            for line in f:
                self.parse_line(line.rstrip('\n'), i)
                i += 1

    def parse_line(self, line, ln):
        for pattern, handler in self.__handlers:
            match = pattern.match(line)
            if match:
                handler(line, ln, match)
                break

    def print_warnings(self):
        for (warning, line, ln) in self.warnings:
            print(f'{self.__filename}:{ln}: {warning}')
            print(f'{ln:4} | {line}')

def main():
    global verbose

    ap = argparse.ArgumentParser(fromfile_prefix_chars='@',
                                 epilog='Arguments can also be passed in a file prefixed with a "@" character.')
    ap.add_argument('dts', nargs='*',
                    help='Filename or directory of devicetree DTS input file(s)')
    ap.add_argument('-v', '--verbose', help='verbose mode', action='store_true')
    args = ap.parse_args()

    verbose = args.verbose

    for d in args.dts:
        if not os.path.isdir(d):
            continue
        for filename in glob.iglob(d + '/**/*.dts[io]?', recursive=True):
            if verbose:
                print('Check:  ' + filename)
            style = DtsStyle(filename)
            style.check_dts()
            style.print_warnings()

    for filename in args.dts:
        if not os.path.isfile(filename):
            continue
        if verbose:
            print('Check:  ' + filename)
        style = DtsStyle(filename)
        style.check_dts()
        style.print_warnings()

if __name__ == '__main__':
    main()
