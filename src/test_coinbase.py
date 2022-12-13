#  test_yahoo.py
#
#  license: GNU LGPL
#
#  This library is free software; you can redistribute it and/or
#  modify it under the terms of the GNU Lesser General Public
#  License as published by the Free Software Foundation; either
#  version 3 of the License, or (at your option) any later version.

import argparse
import logging
import os
import pathlib
import sys
import unittest

logging.basicConfig(level=logging.ERROR, format="%(asctime)s %(name)s %(levelname)s %(message)s")

import financials
from datacode import Datacode
import testutils

financials = financials.createInstance(None)


class Test(unittest.TestCase):

    def test_currency(self):
        s = financials.getRealtime('ETH-EUR', Datacode.LAST_PRICE.value, 'COINBASE')
        self.assertEqual(float, type(s), 'test_currency LAST_PRICE')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('unittest_args', nargs='*')
    args = parser.parse_args()
    unit_argv = [sys.argv[0]] + args.unittest_args
    unittest.main(argv=unit_argv)
