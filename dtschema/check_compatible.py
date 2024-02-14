#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
# Copyright 2022 Arm Ltd.

import os
import argparse

import dtschema


def main():
    ap = argparse.ArgumentParser(fromfile_prefix_chars='@',
        epilog='Arguments can also be passed in a file prefixed with a "@" character.')
    ap.add_argument("compatible_str", nargs='+',
                    help="1 or more compatible strings to check for a match")
    ap.add_argument('-q', '--quiet', action="store_true",
                    help="Suppress printing matches")
    ap.add_argument('-v', '--invert-match', action="store_true",
                    help="invert sense of matching, printing compatible which don't match")
    ap.add_argument('-V', '--version', help="Print version number",
                    action="version", version=dtschema.__version__)
    ap.add_argument('-s', '--schema', required=True, help="path to processed schema file or schema directory")
    args = ap.parse_args()

    if args.schema != "" and not os.path.exists(args.schema):
        exit(-1)

    undoc_compats = dtschema.DTValidator([args.schema]).get_undocumented_compatibles(args.compatible_str)

    if args.invert_match:
        if len(undoc_compats) > 0:
            if not args.quiet:
                print(*undoc_compats, sep="\n")
            return 0
    else:
        matches = set(args.compatible_str).difference(undoc_compats)
        if len(matches) > 0:
            if not args.quiet:
                print(*matches, sep="\n")
            return 0

    return -1
