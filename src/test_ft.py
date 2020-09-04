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
import sys
import unittest

import financials
from datacode import Datacode

financials = financials.createInstance(None)

logging.basicConfig(level=logging.ERROR)


class Test(unittest.TestCase):

    def test_currency(self):
        s = financials.getRealtime('EURGBP', 'LAST_PRICE', 'FT')
        self.assertEqual(type(s), float, 'test_currency LAST_PRICE')

        s = financials.getRealtime('EURGBP', 'CURRENCY', 'FT')
        self.assertEqual(type(s), str, 'test_currency CURRENCY')

    def test_US_equity(self):

        s = financials.getRealtime('INTC:NSQ', 'CHANGE', 'FT')
        self.assertEqual(type(s), float, 'test_US_equity CHANGE {}'.format(s))

        s = financials.getRealtime('INTC:NSQ', 'CHANGE_IN_PERCENT', 'FT')
        self.assertEqual(type(s), float, 'test_US_equity CHANGE_IN_PERCENT {}'.format(s))

        s = financials.getRealtime('INTC:NSQ', 'AVG_DAILY_VOL_3MONTH', 'FT')
        self.assertEqual(type(s), float, 'test_US_equity AVG_DAILY_VOL_3MONTH {}'.format(s))

        s = financials.getRealtime('INTC:NSQ', 'MARKET_CAP', 'FT')
        self.assertEqual(type(s), float, 'test_US_equity MARKET_CAP {}'.format(s))

        s = financials.getRealtime('IBM:NYQ', 'TICKER', 'FT')
        self.assertEqual(type(s), str, 'test_US_equity TICKER {}'.format(s))
        self.assertEqual(s, 'IBM:NYQ', 'test_US_equity TICKER {}'.format(s))

        s = financials.getRealtime('IBM:NYQ', 'PREV_CLOSE', 'FT')
        self.assertEqual(type(s), float, 'test_US_equity PREV_CLOSE {}'.format(s))

        s = financials.getRealtime('IBM:NYQ', 'OPEN', 'FT')
        self.assertEqual(type(s), float, 'test_US_equity OPEN {}'.format(s))

        s = financials.getRealtime('IBM:NYQ', 'LAST_PRICE', 'FT')
        self.assertEqual(type(s), float, 'test_US_equity LAST_PRICE {}'.format(s))

        s = financials.getRealtime('IBM:NYQ', 'LOW', 'FT')
        self.assertEqual(type(s), float, 'test_US_equity LOW {}'.format(s))

        s = financials.getRealtime('IBM:NYQ', 'HIGH', 'FT')
        self.assertEqual(type(s), float, 'test_US_equity HIGH {}'.format(s))

        s = financials.getRealtime('IBM:NYQ', 'VOLUME', 'FT')
        self.assertEqual(type(s), float, 'test_US_equity VOLUME {}'.format(s))

        s = financials.getRealtime('IBM:NYQ', 'NAME', 'FT')
        self.assertEqual(type(s), str, 'test_US_equity NAME {}'.format(s))
        self.assertEqual(s, 'International Business Machines Corp',
                         'test_US_equity NAME {}'.format(s))

        s = financials.getRealtime('IBM:NYQ', 'SECTOR', 'FT')
        self.assertEqual(type(s), str, 'test_US_equity SECTOR {}'.format(s))
        self.assertEqual(s, 'Technology', 'test_US_equity SECTOR {}'.format(s))

        s = financials.getRealtime('IBM:NYQ', 'INDUSTRY', 'FT')
        self.assertEqual(type(s), str, 'test_US_equity INDUSTRY {}'.format(s))
        self.assertEqual(s, 'Software & Computer Services', 'test_US_equity INDUSTRY {}'.format(s))

        s = financials.getRealtime('IBM:NYQ', 'TIMEZONE', 'FT')
        self.assertEqual(type(s), str, 'test_US_equity TIMEZONE {}'.format(s))

    def test_US_mutuals(self):

        s = financials.getRealtime('VGSLX', 'LAST_PRICE', 'FT')
        self.assertEqual(type(s), float, 'test_US_mutuals LAST_PRICE {}'.format(s))

        s = financials.getRealtime('VGSLX', 'NAME', 'FT')
        self.assertEqual(s, "Vanguard Real Estate Index Fund Admiral Shares",
                         'test_US_mutuals NAME {}'.format(s))

        s = financials.getRealtime('VGSLX', 'CURRENCY', 'FT')
        self.assertEqual(s, "USD", 'test_US_mutuals CURRENCY {}'.format(s))

        s = financials.getRealtime('VGSLX', 'CHANGE', 'FT')
        self.assertEqual(type(s), float, 'test_US_mutuals CHANGE {}'.format(s))

        s = financials.getRealtime('VGSLX', 'CHANGE_IN_PERCENT', 'FT')
        self.assertEqual(type(s), float, 'test_US_mutuals CHANGE_IN_PERCENT {}'.format(s))

        s = financials.getRealtime('VFIAX', 'LAST_PRICE', 'FT')
        self.assertEqual(type(s), float, 'test_US_mutuals LAST_PRICE {}'.format(s))

        s = financials.getRealtime('VFIAX', 'LAST_PRICE_DATE', 'FT')
        self.assertEqual(type(s), str, 'test_US_mutuals LAST_PRICE_DATE {}'.format(s))

        s = financials.getRealtime('VFIAX', 'LAST_PRICE_TIME', 'FT')
        self.assertEqual(type(s), str, 'test_US_mutuals LAST_PRICE_TIME {}'.format(s))

    def test_UK_ETF(self):

        s = financials.getRealtime('CSP1:LSE:GBX', 'NAME', 'FT')
        self.assertEqual(type(s), str, 'test_UK_ETF NAME {}'.format(s))
        self.assertEqual(s, 'iShares Core S&P 500 UCITS ETF USD (Acc)',
                         'test_UK_ETF NAME {}'.format(s))

        s = financials.getRealtime('C060:GER:EUR', 'NAME', 'FT')
        self.assertEqual(type(s), str, 't_UK_ETF NAME {}'.format(s))

        s = financials.getRealtime('VERX:LSE:GBP', 'LAST_PRICE', 'FT')
        self.assertEqual(type(s), float, 'test_UK_ETF LAST_PRICE {}'.format(s))

        s = financials.getRealtime('VERX:LSE:GBP', 'TIMEZONE', 'FT')
        self.assertEqual(type(s), str, 'test_UK_ETF TIMEZONE {}'.format(s))

    def test_DE_equity(self):

        s = financials.getRealtime('SAPX:GER', 'NAME', 'FT')
        self.assertEqual(s, "SAP SE", 'test_DE_equity NAME {}'.format(s))

        s = financials.getRealtime('SAPX:GER', 'TICKER', 'FT')
        self.assertEqual(s, "SAPX:GER", 'test_DE_equity TICKER {}'.format(s))

        s = financials.getRealtime('SAPX:GER', 'CURRENCY', 'FT')
        self.assertEqual(s, 'EUR', 'test_DE_equity CURRENCY {}'.format(s))

        s = financials.getRealtime('SAPX:GER', 'LAST_PRICE', 'FT')
        self.assertEqual(type(s), float, 'test_DE_equity LAST_PRICE {}'.format(s))

        s = financials.getRealtime('SAPX:GER', 'CHANGE', 'FT')
        self.assertEqual(type(s), float, 'test_DE_equity CHANGE {}'.format(s))

        s = financials.getRealtime('SAPX:GER', 'CHANGE_IN_PERCENT', 'FT')
        self.assertEqual(type(s), float, 'test_DE_equity CHANGE_IN_PERCENT {}'.format(s))

        s = financials.getRealtime('SAPX:GER', 'VOLUME', 'FT')
        self.assertEqual(type(s), float, 'test_DE_equity VOLUME {}'.format(s))

        s = financials.getRealtime('SAPX:GER', 'OPEN', 'FT')
        self.assertEqual(type(s), float, 'test_DE_equity OPEN {}'.format(s))

        s = financials.getRealtime('SAPX:GER', 'HIGH', 'FT')
        self.assertEqual(type(s), float, 'test_DE_equity HIGH {}'.format(s))

        s = financials.getRealtime('SAPX:GER', 'LOW', 'FT')
        self.assertEqual(type(s), float, 'test_DE_equity LOW {}'.format(s))

        s = financials.getRealtime('SAPX:GER', 'PREV_CLOSE', 'FT')
        self.assertEqual(type(s), float, 'test_DE_equity PREV_CLOSE {}'.format(s))

        s = financials.getRealtime('SAPX:GER', 'MARKET_CAP', 'FT')
        self.assertEqual(type(s), float, 'test_DE_equity MARKET_CAP {}'.format(s))

        s = financials.getRealtime('SAPX:GER', 'SECTOR', 'FT')
        self.assertEqual(type(s), str, 'test_DE_equity SECTOR {}'.format(s))
        self.assertEqual(s, 'Technology', 'test_DE_equity SECTOR {}'.format(s))

        s = financials.getRealtime('SAPX:GER', 'INDUSTRY', 'FT')
        self.assertEqual(type(s), str, 'test_DE_equity INDUSTRY {}'.format(s))
        self.assertEqual(s, 'Software & Computer Services', 'test_DE_equity INDUSTRY {}'.format(s))

        s = financials.getRealtime('SAPX:GER', 'LAST_PRICE_DATE', 'FT')
        self.assertEqual(type(s), str, 'test_DE_equity LAST_PRICE_DATE {}'.format(s))

        s = financials.getRealtime('SAPX:GER', 'TIMEZONE', 'FT')
        self.assertEqual(type(s), str, 'test_DE_equity TIMEZONE {}'.format(s))

    def test_TY_equity(self):
        s = financials.getRealtime('6503:TYO', 'OPEN', 'FT')
        self.assertEqual(type(s), float, 'test_TY_equity OPEN {}'.format(s))

        s = financials.getRealtime('6503:TYO', 'LOW', 'FT')
        self.assertEqual(type(s), float, 'test_TY_equity LOW {}'.format(s))

        s = financials.getRealtime('6503:TYO', 'HIGH', 'FT')
        self.assertEqual(type(s), float, 'test_TY_equity HIGH {}'.format(s))

        s = financials.getRealtime('6503:TYO', 'LOW_52_WEEK', 'FT')
        self.assertEqual(type(s), float, 'test_TY_equity LOW_52_WEEK {}'.format(s))

        s = financials.getRealtime('6503:TYO', 'HIGH_52_WEEK', 'FT')
        self.assertEqual(type(s), float, 'test_TY_equity HIGH_52_WEEK {}'.format(s))

        s = financials.getRealtime('6503:TYO', 'MARKET_CAP', 'FT')
        self.assertEqual(type(s), float, 'test_TY_equity MARKET_CAP {}'.format(s))

        s = financials.getRealtime('6503:TYO', 'VOLUME', 'FT')
        self.assertEqual(type(s), float, 'test_TY_equity VOLUME {}'.format(s))

        s = financials.getRealtime('6503:TYO', 'CURRENCY', 'FT')
        self.assertEqual(s, 'JPY', 'test_TY_equity CURRENCY')

        s = financials.getRealtime('6503:TYO', 'SECTOR', 'FT')
        self.assertEqual(type(s), str, 'test_TY_equity SECTOR {}'.format(s))
        self.assertEqual(s, 'Industrials', 'test_TY_equity SECTOR {}'.format(s))

        s = financials.getRealtime('6503:TYO', 'INDUSTRY', 'FT')
        self.assertEqual(type(s), str, 'test_TY_equity INDUSTRY {}'.format(s))
        self.assertEqual(s, 'General Industrials', 'test_TY_equity INDUSTRY {}'.format(s))

    def test_index(self):

        s = financials.getRealtime('INX:IOM', 'ticker', 'FT')
        self.assertEqual(s, "INX:IOM", 'test_index TICKER {}'.format(s))

        s = financials.getRealtime('DAXX:GER', 'ticker', 'FT')
        self.assertEqual(s, "DAXX:GER", 'test_index TICKER {}'.format(s))

        s = financials.getRealtime('DAXX:GER', 'last_price', 'FT')
        self.assertEqual(type(s), float, 'test_index LAST_PRICE {}'.format(s))

        s = financials.getRealtime('DAXX:GER', 'volume', 'FT')
        self.assertEqual(type(s), float, 'test_DE_equity VOLUME {}'.format(s))

        s = financials.getRealtime('DAXX:GER', 'low_52_week', 'FT')
        self.assertEqual(type(s), float, 'test_DE_equity LOW_52_WEEK {}'.format(s))

        s = financials.getRealtime('DAXX:GER', 'high_52_week', 'FT')
        self.assertEqual(type(s), float, 'test_DE_equity HIGH_52_WEEK {}'.format(s))

        s = financials.getRealtime('DAXX:GER', 'open', 'FT')
        self.assertIsNone(s, 'test_DE_equity OPEN {}'.format(s))

        s = financials.getRealtime('DAXX:GER', 'high', 'FT')
        self.assertIsNone(s, 'test_DE_equity HIGH {}'.format(s))

        s = financials.getRealtime('DAXX:GER', 'low', 'FT')
        self.assertIsNone(s, 'test_DE_equity LOW {}'.format(s))

        s = financials.getRealtime('DAXX:GER', 'prev_close', 'FT')
        self.assertIsNone(s, 'test_DE_equity PREV_CLOSE {}'.format(s))

        s = financials.getRealtime('DAXX:GER', 'market_cap', 'FT')
        self.assertIsNone(s, 'test_DE_equity MARKET_CAP {}'.format(s))

    def test_errors(self):

        s = financials.getRealtime('NO_NAME', 'LAST_PRICE', 'FT')
        self.assertIsNone(s, 'test_errors LAST_PRICE {}'.format(s))

        s = financials.getRealtime('DAXX:GER', 'Foo', 'FT')
        self.assertEqual(s, 'Datacode is invalid', 'test_errors')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('unittest_args', nargs='*')
    args = parser.parse_args()
    unit_argv = [sys.argv[0]] + args.unittest_args
    unittest.main(argv=unit_argv)
