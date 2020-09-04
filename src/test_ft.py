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
        s = financials.getRealtime('EURGBP', Datacode.LAST_PRICE.value, 'FT')
        self.assertEqual(type(s), float, 'test_currency LAST_PRICE')

        s = financials.getRealtime('EURGBP', Datacode.CURRENCY.value, 'FT')
        self.assertEqual(type(s), str, 'test_currency CURRENCY')

    def test_US_equity(self):

        s = financials.getRealtime('INTC:NSQ', Datacode.CHANGE.value, 'FT')
        self.assertEqual(type(s), float, 'test_US_equity CHANGE {}'.format(s))

        s = financials.getRealtime('INTC:NSQ', Datacode.CHANGE_IN_PERCENT.value, 'FT')
        self.assertEqual(type(s), float, 'test_US_equity CHANGE_IN_PERCENT {}'.format(s))

        s = financials.getRealtime('INTC:NSQ', Datacode.AVG_DAILY_VOL_3MONTH.value, 'FT')
        self.assertEqual(type(s), float, 'test_US_equity AVG_DAILY_VOL_3MONTH {}'.format(s))

        s = financials.getRealtime('INTC:NSQ', Datacode.MARKET_CAP.value, 'FT')
        self.assertEqual(type(s), float, 'test_US_equity MARKET_CAP {}'.format(s))

        s = financials.getRealtime('IBM:NYQ', Datacode.TICKER.value, 'FT')
        self.assertEqual(type(s), str, 'test_US_equity TICKER {}'.format(s))
        self.assertEqual(s, 'IBM:NYQ', 'test_US_equity TICKER {}'.format(s))

        s = financials.getRealtime('IBM:NYQ', Datacode.PREV_CLOSE.value, 'FT')
        self.assertEqual(type(s), float, 'test_US_equity PREV_CLOSE {}'.format(s))

        s = financials.getRealtime('IBM:NYQ', Datacode.OPEN.value, 'FT')
        self.assertEqual(type(s), float, 'test_US_equity OPEN {}'.format(s))

        s = financials.getRealtime('IBM:NYQ', Datacode.LAST_PRICE.value, 'FT')
        self.assertEqual(type(s), float, 'test_US_equity LAST_PRICE {}'.format(s))

        s = financials.getRealtime('IBM:NYQ', Datacode.LOW.value, 'FT')
        self.assertEqual(type(s), float, 'test_US_equity LOW {}'.format(s))

        s = financials.getRealtime('IBM:NYQ', Datacode.HIGH.value, 'FT')
        self.assertEqual(type(s), float, 'test_US_equity HIGH {}'.format(s))

        s = financials.getRealtime('IBM:NYQ', Datacode.VOLUME.value, 'FT')
        self.assertEqual(type(s), float, 'test_US_equity VOLUME {}'.format(s))

        s = financials.getRealtime('IBM:NYQ', Datacode.NAME.value, 'FT')
        self.assertEqual(type(s), str, 'test_US_equity NAME {}'.format(s))
        self.assertEqual(s, 'International Business Machines Corp',
                         'test_US_equity NAME {}'.format(s))

        s = financials.getRealtime('IBM:NYQ', Datacode.SECTOR.value, 'FT')
        self.assertEqual(type(s), str, 'test_US_equity SECTOR {}'.format(s))
        self.assertEqual(s, 'Technology', 'test_US_equity SECTOR {}'.format(s))

        s = financials.getRealtime('IBM:NYQ', Datacode.INDUSTRY.value, 'FT')
        self.assertEqual(type(s), str, 'test_US_equity INDUSTRY {}'.format(s))
        self.assertEqual(s, 'Software & Computer Services', 'test_US_equity INDUSTRY {}'.format(s))

        s = financials.getRealtime('IBM:NYQ', Datacode.TIMEZONE.value, 'FT')
        self.assertEqual(type(s), str, 'test_US_equity TIMEZONE {}'.format(s))

    def test_US_mutuals(self):

        s = financials.getRealtime('VGSLX', Datacode.LAST_PRICE.value, 'FT')
        self.assertEqual(type(s), float, 'test_US_mutuals LAST_PRICE {}'.format(s))

        s = financials.getRealtime('VGSLX', Datacode.NAME.value, 'FT')
        self.assertEqual(s, "Vanguard Real Estate Index Fund Admiral Shares",
                         'test_US_mutuals NAME {}'.format(s))

        s = financials.getRealtime('VGSLX', Datacode.CURRENCY.value, 'FT')
        self.assertEqual(s, "USD", 'test_US_mutuals CURRENCY {}'.format(s))

        s = financials.getRealtime('VGSLX', Datacode.CHANGE.value, 'FT')
        self.assertEqual(type(s), float, 'test_US_mutuals CHANGE {}'.format(s))

        s = financials.getRealtime('VGSLX', Datacode.CHANGE_IN_PERCENT.value, 'FT')
        self.assertEqual(type(s), float, 'test_US_mutuals CHANGE_IN_PERCENT {}'.format(s))

        s = financials.getRealtime('VFIAX', Datacode.LAST_PRICE.value, 'FT')
        self.assertEqual(type(s), float, 'test_US_mutuals LAST_PRICE {}'.format(s))

        s = financials.getRealtime('VFIAX', Datacode.LAST_PRICE_DATE.value, 'FT')
        self.assertEqual(type(s), str, 'test_US_mutuals LAST_PRICE_DATE {}'.format(s))

        s = financials.getRealtime('VFIAX', Datacode.LAST_PRICE_TIME.value, 'FT')
        self.assertEqual(type(s), str, 'test_US_mutuals LAST_PRICE_TIME {}'.format(s))

    def test_UK_ETF(self):

        s = financials.getRealtime('CSP1:LSE:GBX', Datacode.NAME.value, 'FT')
        self.assertEqual(type(s), str, 'test_UK_ETF NAME {}'.format(s))
        self.assertEqual(s, 'iShares Core S&P 500 UCITS ETF USD (Acc)',
                         'test_UK_ETF NAME {}'.format(s))

        s = financials.getRealtime('C060:GER:EUR', Datacode.NAME.value, 'FT')
        self.assertEqual(type(s), str, 't_UK_ETF NAME {}'.format(s))

        s = financials.getRealtime('VERX:LSE:GBP', Datacode.LAST_PRICE.value, 'FT')
        self.assertEqual(type(s), float, 'test_UK_ETF LAST_PRICE {}'.format(s))

        s = financials.getRealtime('VERX:LSE:GBP', Datacode.TIMEZONE.value, 'FT')
        self.assertEqual(type(s), str, 'test_UK_ETF TIMEZONE {}'.format(s))

    def test_DE_equity(self):

        s = financials.getRealtime('SAPX:GER', Datacode.NAME.value, 'FT')
        self.assertEqual(s, "SAP SE", 'test_DE_equity NAME {}'.format(s))

        s = financials.getRealtime('SAPX:GER', Datacode.TICKER.value, 'FT')
        self.assertEqual(s, "SAPX:GER", 'test_DE_equity TICKER {}'.format(s))

        s = financials.getRealtime('SAPX:GER', Datacode.CURRENCY.value, 'FT')
        self.assertEqual(s, 'EUR', 'test_DE_equity CURRENCY {}'.format(s))

        s = financials.getRealtime('SAPX:GER', Datacode.LAST_PRICE.value, 'FT')
        self.assertEqual(type(s), float, 'test_DE_equity LAST_PRICE {}'.format(s))

        s = financials.getRealtime('SAPX:GER', Datacode.CHANGE.value, 'FT')
        self.assertEqual(type(s), float, 'test_DE_equity CHANGE {}'.format(s))

        s = financials.getRealtime('SAPX:GER', Datacode.CHANGE_IN_PERCENT.value, 'FT')
        self.assertEqual(type(s), float, 'test_DE_equity CHANGE_IN_PERCENT {}'.format(s))

        s = financials.getRealtime('SAPX:GER', Datacode.VOLUME.value, 'FT')
        self.assertEqual(type(s), float, 'test_DE_equity VOLUME {}'.format(s))

        s = financials.getRealtime('SAPX:GER', Datacode.OPEN.value, 'FT')
        self.assertEqual(type(s), float, 'test_DE_equity OPEN {}'.format(s))

        s = financials.getRealtime('SAPX:GER', Datacode.HIGH.value, 'FT')
        self.assertEqual(type(s), float, 'test_DE_equity HIGH {}'.format(s))

        s = financials.getRealtime('SAPX:GER', Datacode.LOW.value, 'FT')
        self.assertEqual(type(s), float, 'test_DE_equity LOW {}'.format(s))

        s = financials.getRealtime('SAPX:GER', Datacode.PREV_CLOSE.value, 'FT')
        self.assertEqual(type(s), float, 'test_DE_equity PREV_CLOSE {}'.format(s))

        s = financials.getRealtime('SAPX:GER', Datacode.MARKET_CAP.value, 'FT')
        self.assertEqual(type(s), float, 'test_DE_equity MARKET_CAP {}'.format(s))

        s = financials.getRealtime('SAPX:GER', Datacode.SECTOR.value, 'FT')
        self.assertEqual(type(s), str, 'test_DE_equity SECTOR {}'.format(s))
        self.assertEqual(s, 'Technology', 'test_DE_equity SECTOR {}'.format(s))

        s = financials.getRealtime('SAPX:GER', Datacode.INDUSTRY.value, 'FT')
        self.assertEqual(type(s), str, 'test_DE_equity INDUSTRY {}'.format(s))
        self.assertEqual(s, 'Software & Computer Services', 'test_DE_equity INDUSTRY {}'.format(s))

        s = financials.getRealtime('SAPX:GER', Datacode.LAST_PRICE_DATE.value, 'FT')
        self.assertEqual(type(s), str, 'test_DE_equity LAST_PRICE_DATE {}'.format(s))

        s = financials.getRealtime('SAPX:GER', Datacode.TIMEZONE.value, 'FT')
        self.assertEqual(type(s), str, 'test_DE_equity TIMEZONE {}'.format(s))

    def test_TY_equity(self):
        s = financials.getRealtime('6503:TYO', Datacode.OPEN.value, 'FT')
        self.assertEqual(type(s), float, 'test_TY_equity OPEN {}'.format(s))

        s = financials.getRealtime('6503:TYO', Datacode.LOW.value, 'FT')
        self.assertEqual(type(s), float, 'test_TY_equity LOW {}'.format(s))

        s = financials.getRealtime('6503:TYO', Datacode.HIGH.value, 'FT')
        self.assertEqual(type(s), float, 'test_TY_equity HIGH {}'.format(s))

        s = financials.getRealtime('6503:TYO', Datacode.LOW_52_WEEK.value, 'FT')
        self.assertEqual(type(s), float, 'test_TY_equity LOW_52_WEEK {}'.format(s))

        s = financials.getRealtime('6503:TYO', Datacode.HIGH_52_WEEK.value, 'FT')
        self.assertEqual(type(s), float, 'test_TY_equity HIGH_52_WEEK {}'.format(s))

        s = financials.getRealtime('6503:TYO', Datacode.MARKET_CAP.value, 'FT')
        self.assertEqual(type(s), float, 'test_TY_equity MARKET_CAP {}'.format(s))

        s = financials.getRealtime('6503:TYO', Datacode.VOLUME.value, 'FT')
        self.assertEqual(type(s), float, 'test_TY_equity VOLUME {}'.format(s))

        s = financials.getRealtime('6503:TYO', Datacode.CURRENCY.value, 'FT')
        self.assertEqual(s, 'JPY', 'test_TY_equity CURRENCY')

        s = financials.getRealtime('6503:TYO', Datacode.SECTOR.value, 'FT')
        self.assertEqual(type(s), str, 'test_TY_equity SECTOR {}'.format(s))
        self.assertEqual(s, 'Industrials', 'test_TY_equity SECTOR {}'.format(s))

        s = financials.getRealtime('6503:TYO', Datacode.INDUSTRY.value, 'FT')
        self.assertEqual(type(s), str, 'test_TY_equity INDUSTRY {}'.format(s))
        self.assertEqual(s, 'General Industrials', 'test_TY_equity INDUSTRY {}'.format(s))

    def test_index(self):

        s = financials.getRealtime('INX:IOM', Datacode.TICKER.value, 'FT')
        self.assertEqual(s, "INX:IOM", 'test_index TICKER {}'.format(s))

        s = financials.getRealtime('DAXX:GER', Datacode.TICKER.value, 'FT')
        self.assertEqual(s, "DAXX:GER", 'test_index TICKER {}'.format(s))

        s = financials.getRealtime('DAXX:GER', Datacode.LAST_PRICE.value, 'FT')
        self.assertEqual(type(s), float, 'test_index LAST_PRICE {}'.format(s))

        s = financials.getRealtime('DAXX:GER', Datacode.VOLUME.value, 'FT')
        self.assertEqual(type(s), float, 'test_DE_equity VOLUME {}'.format(s))

        s = financials.getRealtime('DAXX:GER', Datacode.LOW_52_WEEK.value, 'FT')
        self.assertEqual(type(s), float, 'test_DE_equity LOW_52_WEEK {}'.format(s))

        s = financials.getRealtime('DAXX:GER', Datacode.HIGH_52_WEEK.value, 'FT')
        self.assertEqual(type(s), float, 'test_DE_equity HIGH_52_WEEK {}'.format(s))

        s = financials.getRealtime('DAXX:GER', Datacode.OPEN.value, 'FT')
        self.assertIsNone(s, 'test_DE_equity OPEN {}'.format(s))

        s = financials.getRealtime('DAXX:GER', Datacode.HIGH.value, 'FT')
        self.assertIsNone(s, 'test_DE_equity HIGH {}'.format(s))

        s = financials.getRealtime('DAXX:GER', Datacode.LOW.value, 'FT')
        self.assertIsNone(s, 'test_DE_equity LOW {}'.format(s))

        s = financials.getRealtime('DAXX:GER', Datacode.PREV_CLOSE.value, 'FT')
        self.assertIsNone(s, 'test_DE_equity PREV_CLOSE {}'.format(s))

        s = financials.getRealtime('DAXX:GER', Datacode.MARKET_CAP.value, 'FT')
        self.assertIsNone(s, 'test_DE_equity MARKET_CAP {}'.format(s))

    def test_errors(self):

        s = financials.getRealtime('NO_NAME', Datacode.LAST_PRICE.value, 'FT')
        self.assertIsNone(s, 'test_errors LAST_PRICE {}'.format(s))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('unittest_args', nargs='*')
    args = parser.parse_args()
    unit_argv = [sys.argv[0]] + args.unittest_args
    unittest.main(argv=unit_argv)
