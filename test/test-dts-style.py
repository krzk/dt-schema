#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
#
# Testcases for the Devicetree sources style tool
#

import unittest
import os

import dtschema

basedir = os.path.dirname(__file__)

class TestDTMetaSchema(unittest.TestCase):
    maxDiff = 4096

    def test_nonexistingfile(self):
        style = dtschema.DtsStyle('does-not-exist-foo-bar.dts')
        with self.assertRaises(FileNotFoundError):
            style.check_dts()

    def test_dtsfile_iterator(self):
        filename = os.path.join(basedir, 'style/dtsfile.dts')
        with dtschema.DtsFile(filename) as f:
            self.assertEqual(str(f), filename)
            (line, lineno) = next(f)
            self.assertEqual(lineno, 1)
            self.assertEqual(line.rstrip(), '// SPDX-License-Identifier: BSD-2-Clause')
            (line, lineno) = next(f)
            self.assertEqual(lineno, 2)
            self.assertEqual(line.rstrip(), '/dts-v1/;')
            (line, lineno) = next(f)
            self.assertEqual(lineno, 3)
            self.assertEqual(line.rstrip(), '/ {')
            (line, lineno) = next(f)
            self.assertEqual(lineno, 4)
            self.assertEqual(line.rstrip(), '	// foo')
            (line, lineno) = next(f)
            self.assertEqual(lineno, 5)
            self.assertEqual(line.rstrip(), '};')

    def test_nodename(self):
        expected = [
            ['Whitespace error', '\tinterrupt-controller-3  {', 23],
            ['Whitespace error', '\tintc_4: interrupt-controller-4  {', 27],
            ['Label: use underscores instead of hyphens', '\tintc-5: interrupt-controller-5  {', 31],
            ['Whitespace error', '\tintc-5: interrupt-controller-5  {', 31],
            ['Whitespace error', '\tintc_6:  interrupt-controller-6 {', 35],
            ['Whitespace error', '\tintc_7:interrupt_controller-7 {', 39],
            ['Node name: use hyphens instead of underscores', '\tintc_7:interrupt_controller-7 {', 39],
            ['Label: only lowercase letters', '\tintC_8: interrupt-controller-8 {', 43],
            ['Nodes do not look sorted alphanumerically', '\tintC_8: interrupt-controller-8 {', 43],
            ['Node name: only lowercase letters', '\tintc_9: interrupt-controlleR-9 {', 47],
            ['Nodes do not look sorted alphanumerically', '\tintc_9: interrupt-controlleR-9 {', 47],
            ['Node name: only lowercase letters', '\tinterrupt-controlleR-10 {', 51],
            # FIXME: switch to natural sorting
            ['Nodes do not look sorted alphanumerically', '\tinterrupt-controlleR-10 {', 51],
            ['Node name: only lowercase letters', '\tinterrupt-controlleR-11 { // Comment', 55],
            ['Node name: only lowercase letters', '\tinterrupt-controlleR-12 { /* Comment */', 59],
        ]
        style = dtschema.DtsStyle(os.path.join(basedir, 'style/nodename.dts'))
        style.check_dts()
        self.assertListEqual(style.warnings, expected)

    def test_nodename_unitaddr(self):
        expected = [
            ['Whitespace error', '\tinterrupt-controller@ff3  {', 40],
            ['Whitespace error', '\tintc_4_2: interrupt-controller@ff4  {', 45],
            ['Label: use underscores instead of hyphens', '\tintc-5_2: interrupt-controller@ff5  {', 50],
            ['Whitespace error', '\tintc-5_2: interrupt-controller@ff5  {', 50],
            ['Whitespace error', '\tintc_6_2:  interrupt-controller@ff6 {', 55],
            ['Whitespace error', '\tintc_7_2:interrupt_controller@ff7 {', 60],
            ['Node name: use hyphens instead of underscores', '\tintc_7_2:interrupt_controller@ff7 {', 60],
            ['Label: only lowercase letters', '\tintC_8_2: interrupt-controller@ff8 {', 65],
            ['Node name: only lowercase letters', '\tintc_9_2: interrupt-controlleR@ff9 {', 70],
            ['Node name: only lowercase letters', '\tinterrupt-controlleR@fff0 { // Comment', 75],
            ['Node name: only lowercase letters', '\tinterrupt-controlleR@fff4 { /* Comment */', 80],
            ['Unit address: avoid leading "0"', '\tinterrupt-controller@0fffa {', 85],
        ]
        style = dtschema.DtsStyle(os.path.join(basedir, 'style/nodename-unitaddr.dts'))
        style.check_dts()
        self.assertListEqual(style.warnings, expected)

    def test_nodeoverride(self):
        expected = [
            ['Whitespace error', '&intc_3  {', 28],
            ['Whitespace error', '&intc_3  { // Comment', 32],
            ['Whitespace error', '&intc_3  { /* Comment */', 36],
            ['Whitespace error', '  &intc_4 {', 40],
            ['Label: use underscores instead of hyphens', '&intc-5 {', 44],
            ['Node overrides do not look sorted alphanumerically', '&intc-5 {', 44],
            ['Label: only lowercase letters', '&intC_6 {', 48],
            ['Node overrides do not look sorted alphanumerically', '&intC_6 {', 48],
            ['Node name: only lowercase letters', '\tINTERRUPT-controller-1 {', 55],
            ['Node name: only lowercase letters', '\tINTERRUPT-controller-2 { // Comment', 59],
            ['Node name: only lowercase letters', '\tINTERRUPT-controller-3 { /* Comment */', 63],
        ]
        style = dtschema.DtsStyle(os.path.join(basedir, 'style/nodeoverride.dts'))
        style.check_dts()
        self.assertListEqual(style.warnings, expected)

    def test_nodeorder_label(self):
        expected = [
            ['Node overrides do not look sorted alphanumerically', '&a_error {', 26],
            ['Node overrides do not look sorted alphanumerically', '&a_also_error_1 { // Comment', 30],
            ['Node overrides do not look sorted alphanumerically', '&a_also_error_2 { /* Comment */', 38],
            ['Label: use underscores instead of hyphens', '&b_error-also-wrong-name {', 54],
            ['Node overrides do not look sorted alphanumerically', '&b_error-also-wrong-name {', 54],
        ]
        style = dtschema.DtsStyle(os.path.join(basedir, 'style/nodeorder-label.dts'))
        style.check_dts()
        self.assertListEqual(style.warnings, expected)

    def test_nodeorder_mixed(self):
        expected = [
            ['Nodes do not look sorted alphanumerically', '\ta-error {', 21],
            ['Nodes do not look sorted by unit address', '\ta-error@30 {', 45],
            ['Nodes do not look sorted by unit address', '\ta-error@20 { // Comment', 50],
            ['Nodes do not look sorted by unit address', '\ta-error@10 { /* Comment */', 55],
            # Uncomment if check in DtsStyle is enabled
            # ['Nodes without unit addresses should preceed nodes with unit address', '\tb-error {', 40],
        ]
        style = dtschema.DtsStyle(os.path.join(basedir, 'style/nodeorder-mixed.dts'))
        style.check_dts()
        self.assertListEqual(style.warnings, expected)

    def test_nodeorder_name(self):
        expected = [
            ['Nodes do not look sorted alphanumerically', '\ta-error {', 21],
            ['Nodes do not look sorted alphanumerically', '\ta-also-error-2 { // Comment', 25],
            ['Nodes do not look sorted alphanumerically', '\ta-also-error-1 { /* Comment */', 29],
            ['Node name: use hyphens instead of underscores', '\tb-error_also_wrong_name {', 45],
            ['Nodes do not look sorted alphanumerically', '\tb-error_also_wrong_name {', 45],
        ]
        style = dtschema.DtsStyle(os.path.join(basedir, 'style/nodeorder-name.dts'))
        style.check_dts()
        self.assertListEqual(style.warnings, expected)

    def test_nodeorder_unitaddr(self):
        expected = [
            ['Nodes do not look sorted by unit address', '\ta-error@30 {', 43],
            ['Nodes do not look sorted by unit address', '\ta-error@20 { // Comment', 48],
            ['Nodes do not look sorted by unit address', '\ta-error@10 { /* Comment */', 53],
            ['Nodes do not look sorted by unit address', '\td-error@24 {', 63],
        ]
        style = dtschema.DtsStyle(os.path.join(basedir, 'style/nodeorder-unitaddr.dts'))
        style.check_dts()
        self.assertListEqual(style.warnings, expected)

if __name__ == '__main__':
    unittest.main()
