#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause

import argparse
import glob
import os
import re

verbose = False

class DtsFile():
    def __init__(self, filename):
        self.filename = filename
        self.lineno = 0
        self.__file = None

    def __enter__(self):
        self.__file = open(self.filename, 'r')
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.__file is not None:
            self.__file.close()

    def __iter__(self):
        return self

    def __next__(self):
        a = next(self.__file)
        self.lineno += 1
        return (a, self.lineno)

    def __str__(self):
        return self.filename

class DtsStyle():
    def __init__(self, filename):
        self.warnings = []
        self.__filename = filename
        self.__nested = 0
        self.__prev_node = {}
        self.__handlers = [
            (re.compile(r'^\s*(?P<label>[a-zA-Z0-9,_-]+:)?(?P<s1>\s*)(?P<nodename>[a-zA-Z0-9,_-]+)(@(?P<unitaddr>[0-9a-fA-FxX]+))?(?P<s2>\s*)\{(?P<s3>\s*)$'),
             self.handle_node),
            (re.compile(r'^(?P<s1>\s*)(?P<label>&[a-zA-Z0-9,_-]+)?(?P<s2>\s*)\{(?P<s3>\s*)$'),
             self.handle_node_extend),
            (re.compile(r'^.*\{.*$'), self.handle_open_node),
            (re.compile(r'^.*\};(?P<s1>\s*)$'), self.handle_close_node),
            ]
        if filename.endswith('.diff') or filename.endswith('.patch'):
            # TODO: handle diff/patch
            raise Exception('Cannot handle diff/patch files yet, pass DTS/DTSI/DTSO only')

    def check_node_sorting(self, line, ln, node):
        if not self.__nested in self.__prev_node:
            return
        prev_node = self.__prev_node[self.__nested]
        if node['label'] and prev_node['label']:
            if node['label'] < prev_node['label']:
                self.warnings.append(['Node overrides do not look sorted alphanumerically', line, ln])
            return
        elif node['unitaddr'] and prev_node['unitaddr']:
            # FIXME: handle conversion error
            if int(node['unitaddr'], 16) < int(prev_node['unitaddr'], 16):
                self.warnings.append(['Nodes do not look sorted by unit address', line, ln])
            return
        elif node['nodename'] and prev_node['nodename']:
            if node['nodename'] and prev_node['unitaddr']:
                # TODO: questionable, known exceptions for cpus
                # self.warnings.append(['Nodes without unit addresses should preceed nodes with unit address', line, ln])
                pass
            elif node['nodename'] < prev_node['nodename']:
                # Enforce node sorting by name only for top-level nodes, because
                # children of many devices, e.g. thermal trips or pin muxes follow different
                # style, so skip nesting of top-level nodes and nesting within node
                # overrides (by label)
                override_by_label = False
                if (self.__nested - 1) in self.__prev_node:
                    override_by_label = self.__prev_node[self.__nested - 1]['label'] != ''
                if self.__nested < 2 and not override_by_label:
                    self.warnings.append(['Nodes do not look sorted alphanumerically', line, ln])
            return
        self.warnings.append(['Dunno how to handle this yet', line, ln])

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
        node = {
            'nodename': nodename,
            'unitaddr': unitaddr,
            'label': '',
        }
        self.check_node_sorting(line, ln, node)
        self.__prev_node[self.__nested] = node
        self.__nested += 1

    def check_label(self, line, ln, match):
        label = match.group('label')
        if match.group('s1') or match.group('s2') != ' ' or match.group('s3'):
            self.warnings.append(['Whitespace error', line, ln])
        if '-' in label:
            self.warnings.append(['Label: use underscores instead of hyphens', line, ln])
        if re.search('[A-Z]', label):
            self.warnings.append(['Label: only lowercase letters', line, ln])
        node = {
            'nodename': '',
            'unitaddr': '',
            'label': label,
        }
        self.check_node_sorting(line, ln, node)
        self.__prev_node[self.__nested] = node
        self.__nested += 1

    def handle_node(self, line, ln, match):
        self.check_node_name(line, ln, match)

    def handle_node_extend(self, line, ln, match):
        self.check_label(line, ln, match)

    def handle_open_node(self, line, ln, match):
        self.__nested += 1

    def handle_close_node(self, line, ln, match):
        if self.__nested in self.__prev_node:
            del self.__prev_node[self.__nested]
        self.__nested -= 1

    def check_dts(self):
        """Check the given DTS/DTSI/DTSO for style"""
        with DtsFile(self.__filename) as f:
            for (line, lineno) in f:
                self.parse_line(line.rstrip('\n'), lineno)

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
