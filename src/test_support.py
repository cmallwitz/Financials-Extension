#  test_google.py
#
#  license: GNU LGPL
#
#  This library is free software; you can redistribute it and/or
#  modify it under the terms of the GNU Lesser General Public
#  License as published by the Free Software Foundation; either
#  version 3 of the License, or (at your option) any later version.

import argparse
import logging
import sys
import unittest

logging.basicConfig(level=logging.ERROR, format="%(asctime)s %(name)s %(levelname)s %(message)s")

import financials

financials = financials.createInstance(None)


class Test(unittest.TestCase):

    def test_support(self):
        cell_range = ((1, 2), ('3', '4'), (5.0, 6.0))

        s = financials.getRealtime('SUPPORT')
        self.assertTrue(s.startswith("ctx="), 'test_errors SUPPORT {}'.format(s))
        self.assertTrue("version=3.0.0" in s, 'test_errors SUPPORT {}'.format(s))

        s = financials.getRealtime('SUPPORT', 1)
        self.assertTrue(s.startswith("ctx="), 'test_errors SUPPORT {}'.format(s))
        self.assertTrue("type(datacode)=<class 'int'>" in s, 'test_errors SUPPORT {}'.format(s))
        self.assertTrue("str(datacode)=1" in s, 'test_errors SUPPORT {}'.format(s))

        s = financials.getRealtime('SUPPORT', 1.0)
        self.assertTrue(s.startswith("ctx="), 'test_errors SUPPORT {}'.format(s))
        self.assertTrue("type(datacode)=<class 'float'>" in s, 'test_errors SUPPORT {}'.format(s))
        self.assertTrue("str(datacode)=1.0" in s, 'test_errors SUPPORT {}'.format(s))

        s = financials.getRealtime('SUPPORT', '1')
        self.assertTrue(s.startswith("ctx="), 'test_errors SUPPORT {}'.format(s))
        self.assertTrue("type(datacode)=<class 'str'>" in s, 'test_errors SUPPORT {}'.format(s))
        self.assertTrue("str(datacode)=1" in s, 'test_errors SUPPORT {}'.format(s))

        s = financials.getRealtime('SUPPORT', cell_range)
        self.assertTrue(s.startswith("ctx="), 'test_errors SUPPORT {}'.format(s))
        self.assertTrue("type(datacode)=<class 'tuple'>" in s, 'test_errors SUPPORT {}'.format(s))
        self.assertTrue("str(datacode)=((1, 2), ('3', '4'), (5.0, 6.0))" in s, 'test_errors SUPPORT {}'.format(s))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('unittest_args', nargs='*')
    args = parser.parse_args()
    unit_argv = [sys.argv[0]] + args.unittest_args
    unittest.main(argv=unit_argv)
