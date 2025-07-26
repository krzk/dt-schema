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
            ['Whitespace error', '\tinterrupt-controller-3  {', 38],
            ['Whitespace error', '\tintc_4: interrupt-controller-4  {', 42],
            ['Label: use underscores instead of hyphens', '\tintc-5: interrupt-controller-5  {', 46],
            ['Whitespace error', '\tintc-5: interrupt-controller-5  {', 46],
            ['Whitespace error', '\tintc_6:  interrupt-controller-6 {', 50],
            ['Whitespace error', '\tintc_7:interrupt_controller-7 {', 54],
            ['Node name: use hyphens instead of underscores', '\tintc_7:interrupt_controller-7 {', 54],
            ['Label: only lowercase letters', '\tintC_8: interrupt-controller-8 {', 58],
            ['Node name: only lowercase letters', '\tintc_9: interrupt-controlleR-9 {', 62],
            ['Node name: only lowercase letters', '\tinterrupt-controlleR-10 {', 66],
            ['Whitespace error', '\tinterrupt-controller@3  {', 70],
            ['Whitespace error', '\tintc_4_2: interrupt-controller@4  {', 75],
            ['Label: use underscores instead of hyphens', '\tintc-5_2: interrupt-controller@5  {', 80],
            ['Whitespace error', '\tintc-5_2: interrupt-controller@5  {', 80],
            ['Whitespace error', '\tintc_6_2:  interrupt-controller@6 {', 85],
            ['Whitespace error', '\tintc_7_2:interrupt_controller@7 {', 90],
            ['Node name: use hyphens instead of underscores', '\tintc_7_2:interrupt_controller@7 {', 90],
            ['Label: only lowercase letters', '\tintC_8_2: interrupt-controller@8 {', 95],
            ['Node name: only lowercase letters', '\tintc_9_2: interrupt-controlleR@9 {', 100],
            ['Unit address: avoid leading "0"', '\tinterrupt-controller@0a {', 105],
        ]
        style = dtschema.DtsStyle(os.path.join(basedir, 'style/nodename.dts'))
        style.check_dts()
        self.assertListEqual(style.warnings, expected)

if __name__ == '__main__':
    unittest.main()
