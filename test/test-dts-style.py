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
            ['Nodes do not look sorted alphanumerically', '\tinterrupt-controlleR-10 {', 51],
        ]
        style = dtschema.DtsStyle(os.path.join(basedir, 'style/nodename.dts'))
        style.check_dts()
        self.assertListEqual(style.warnings, expected)

    def test_nodename_unitaddr(self):
        expected = [
            ['Whitespace error', '\tinterrupt-controller@ff3  {', 30],
            ['Whitespace error', '\tintc_4_2: interrupt-controller@ff4  {', 35],
            ['Label: use underscores instead of hyphens', '\tintc-5_2: interrupt-controller@ff5  {', 40],
            ['Whitespace error', '\tintc-5_2: interrupt-controller@ff5  {', 40],
            ['Whitespace error', '\tintc_6_2:  interrupt-controller@ff6 {', 45],
            ['Whitespace error', '\tintc_7_2:interrupt_controller@ff7 {', 50],
            ['Node name: use hyphens instead of underscores', '\tintc_7_2:interrupt_controller@ff7 {', 50],
            ['Label: only lowercase letters', '\tintC_8_2: interrupt-controller@ff8 {', 55],
            ['Node name: only lowercase letters', '\tintc_9_2: interrupt-controlleR@ff9 {', 60],
            ['Unit address: avoid leading "0"', '\tinterrupt-controller@0ffa {', 65],
        ]
        style = dtschema.DtsStyle(os.path.join(basedir, 'style/nodename-unitaddr.dts'))
        style.check_dts()
        self.assertListEqual(style.warnings, expected)

    def test_nodeoverride(self):
        expected = [
            ['Whitespace error', '&intc_3  {', 28],
            ['Whitespace error', '  &intc_4 {', 32],
            ['Label: use underscores instead of hyphens', '&intc-5 {', 36],
            ['Label: only lowercase letters', '&intC_6 {', 40],
            ['Node name: only lowercase letters', '\tINTERRUPT-controller-1 {', 47],
        ]
        style = dtschema.DtsStyle(os.path.join(basedir, 'style/nodeoverride.dts'))
        style.check_dts()
        self.assertListEqual(style.warnings, expected)

if __name__ == '__main__':
    unittest.main()
