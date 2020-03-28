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

import financials
from datacode import Datacode

financials = financials.createInstance(None)

logging.basicConfig(level=logging.ERROR)


class Test(unittest.TestCase):

    def test_currency(self):
        s = financials.getRealtime('EURGBP', Datacode.LAST_PRICE.value, 'GOOGLE')
        self.assertEqual('Google.getRealtime(EURGBP, 21) - no match', s, 'test_currency LAST_PRICE')

        # s = financials.getRealtime('EURGBP', Datacode.CURRENCY.value, 'GOOGLE')
        # self.assertEqual(type(s), str, 'test_currency CURRENCY')
        # self.assertEqual(s, '', 'test_currency CURRENCY')

    def test_UK_equity(self):
        s = financials.getRealtime('LON:VOD', Datacode.LAST_PRICE.value, 'GOOGLE')
        self.assertEqual(type(s), float, 'test_UK_equity LAST_PRICE {}'.format(s))

        s = financials.getRealtime('LON:VOD', Datacode.TICKER.value, 'GOOGLE')
        self.assertEqual(s, 'VOD', 'test_UK_equity TICKER')

        s = financials.getRealtime('LON:VOD', Datacode.NAME.value, 'GOOGLE')
        self.assertEqual(type(s), str, 'test_UK_equity NAME')

        s = financials.getRealtime('LON:VOD', Datacode.EXCHANGE.value, 'GOOGLE')
        self.assertEqual(s, 'LON', 'test_UK_equity EXCHANGE')

        s = financials.getRealtime('LON:VOD', Datacode.PREV_CLOSE.value, 'GOOGLE')
        self.assertEqual(type(s), float, 'test_UK_equity PREV_CLOSE {}'.format(s))

        # MARKET_CAP missing for UK stock but available for German stock - weekend issue (FX) ?
        s = financials.getRealtime('LON:VOD', Datacode.MARKET_CAP.value, 'GOOGLE')
        self.assertEqual(type(s), float, 'test_UK_equity MARKET_CAP {}'.format(s))

    def test_UK_ETF(self):
        s = financials.getRealtime('LON:CSP1', Datacode.LAST_PRICE.value, 'GOOGLE')
        self.assertEqual(type(s), float, 'test_UK_ETF LAST_PRICE {}'.format(s))

        s = financials.getRealtime('LON:CSP1', Datacode.CURRENCY.value, 'GOOGLE')
        self.assertEqual(s, 'GBX', 'test_UK_ETF CURRENCY')

        s = financials.getRealtime('LON:FTAL', Datacode.LAST_PRICE.value, 'GOOGLE')
        self.assertEqual(type(s), float, 'test_UK_ETF LAST_PRICE {}'.format(s))

        s = financials.getRealtime('LON:FTAL', Datacode.CURRENCY.value, 'GOOGLE')
        self.assertEqual(s, 'GBP', 'test_UK_ETF CURRENCY')

        s = financials.getRealtime('LON:FTAL', Datacode.NAME.value, 'GOOGLE')
        self.assertEqual(type(s), str, 'test_UK_ETF NAME')

    def test_DE_equity(self):
        s = financials.getRealtime('FRA:SAP', 7, 'GOOGLE')
        self.assertEqual(type(s), float, 'test_DE_equity 7')

        s = financials.getRealtime('FRA:SAP', '7', 'GOOGLE')
        self.assertEqual(type(s), float, 'test_DE_equity \'7\'')

        s = financials.getRealtime('FRA:SAP', 8, 'GOOGLE')
        self.assertEqual(type(s), str, 'test_DE_equity 8')

        s = financials.getRealtime('FRA:SAP', 8.1, 'GOOGLE')
        self.assertEqual(type(s), str, 'test_DE_equity 8.1')

        s = financials.getRealtime('FRA:SAP', '8.1', 'GOOGLE')
        self.assertEqual(type(s), str, 'test_DE_equity \'8.1\'')

        s = financials.getRealtime('FRA:SAP', 10, 'GOOGLE')
        self.assertEqual(type(s), str, 'test_DE_equity 10')

        s = financials.getRealtime('FRA:SAP', '11', 'GOOGLE')
        self.assertEqual(type(s), float, 'test_DE_equity \'11\'')

        s = financials.getRealtime('FRA:SAP', '21', 'GOOGLE')
        self.assertEqual(type(s), float, 'test_DE_equity \'21\'')

        s = financials.getRealtime('FRA:SAP', Datacode.TIMEZONE.value, 'GOOGLE')
        # self.assertEqual(s, 'Europe/Berlin', 'test_DE_equity TIMEZONE')
        self.assertTrue(s == 'CET' or s == 'CEST', 'test_DE_equity TIMEZONE: {}'.format(s))

    def test_DE_ETF(self):
        s = financials.getRealtime('FRA:C060', Datacode.LAST_PRICE.value, 'GOOGLE')
        self.assertEqual(type(s), float, 'test_DE_ETF LAST_PRICE {}'.format(s))

        s = financials.getRealtime('FRA:C060', Datacode.CURRENCY.value, 'GOOGLE')
        self.assertEqual(s, 'EUR', 'test_DE_ETF CURRENCY')

        s = financials.getRealtime('FRA:C060', Datacode.TICKER.value, 'GOOGLE')
        self.assertEqual(s, 'C060', 'test_DE_ETF TICKER')

        s = financials.getRealtime('FRA:C060', Datacode.EXCHANGE.value, 'GOOGLE')
        self.assertEqual(s, 'FRA', 'test_DE_ETF EXCHANGE')

        s = financials.getRealtime('FRA:C060', Datacode.CURRENCY.value, 'GOOGLE')
        self.assertEqual(s, 'EUR', 'test_DE_ETF CURRENCY')

        s = financials.getRealtime('FRA:C060', Datacode.MARKET_CAP.value, 'GOOGLE')
        self.assertEqual(s, 'Data doesn\'t exist - 27', 'test_DE_ETF TIMESTAMP {}'.format(s))

    def test_TY_equity(self):
        s = financials.getRealtime('TYO:6503', Datacode.OPEN.value, 'GOOGLE')
        self.assertEqual(type(s), float, 'test_TY_equity OPEN {}'.format(s))

        s = financials.getRealtime('TYO:6503', Datacode.LOW.value, 'GOOGLE')
        self.assertEqual(type(s), float, 'test_TY_equity LOW {}'.format(s))

        s = financials.getRealtime('TYO:6503', Datacode.HIGH.value, 'GOOGLE')
        self.assertEqual(type(s), float, 'test_TY_equity HIGH {}'.format(s))

        s = financials.getRealtime('TYO:6503', Datacode.LOW_52_WEEK.value, 'GOOGLE')
        self.assertEqual(type(s), float, 'test_TY_equity LOW_52_WEEK {}'.format(s))

        s = financials.getRealtime('TYO:6503', Datacode.HIGH_52_WEEK.value, 'GOOGLE')
        self.assertEqual(type(s), float, 'test_TY_equity HIGH_52_WEEK {}'.format(s))

        s = financials.getRealtime('TYO:6503', Datacode.MARKET_CAP.value, 'GOOGLE')
        self.assertEqual(type(s), float, 'test_TY_equity MARKET_CAP {}'.format(s))

        # s = financials.getRealtime('TYO:6503', Datacode.VOLUME.value, 'GOOGLE')
        # self.assertEqual(type(s), float, 'test_TY_equity VOLUME {}'.format(s))

        s = financials.getRealtime('TYO:6503', Datacode.CURRENCY.value, 'GOOGLE')
        self.assertEqual(s, 'JPY', 'test_TY_equity CURRENCY')

    def test_US_equity(self):
        s = financials.getRealtime(' NASDAQ : AAPL ', Datacode.LAST_PRICE.value, 'GOOGLE')
        self.assertEqual(type(s), float, 'test_US_equity LAST_PRICE {}'.format(s))

        s = financials.getRealtime(' NASDAQ : AAPL ', Datacode.TICKER.value, 'GOOGLE')
        self.assertEqual(s, 'AAPL', 'test_US_equity TICKER')

        s = financials.getRealtime(' NASDAQ : AAPL ', Datacode.EXCHANGE.value, 'GOOGLE')
        self.assertEqual(s, 'NASDAQ', 'test_US_equity EXCHANGE')

        s = financials.getRealtime(' NASDAQ : AAPL ', Datacode.CURRENCY.value, 'GOOGLE')
        self.assertEqual(s, 'USD', 'test_US_equity CURRENCY')

        s = financials.getRealtime('NYSE:IBM', Datacode.LAST_PRICE.value, 'GOOGLE')
        self.assertEqual(type(s), float, 'test_US_equity LAST_PRICE {}'.format(s))

        s = financials.getRealtime('NYSE:IBM', Datacode.TICKER.value, 'GOOGLE')
        self.assertEqual(s, 'IBM', 'test_US_equity TICKER')

        s = financials.getRealtime('NYSE:IBM', Datacode.EXCHANGE.value, 'GOOGLE')
        self.assertEqual(s, 'NYSE', 'test_US_equity EXCHANGE')

        s = financials.getRealtime('NYSE:IBM', Datacode.CURRENCY.value, 'GOOGLE')
        self.assertEqual(s, 'USD', 'test_US_equity CURRENCY')

        s = financials.getRealtime('NYSE:IBM', Datacode.NAME.value, 'GOOGLE')
        self.assertEqual(type(s), str, 'test_US_equity NAME')
        self.assertEqual(s, 'IBM Common Stock', 'test_US_equity NAME')

        s = financials.getRealtime('NYSE:IBM', Datacode.LOW.value, 'GOOGLE')
        self.assertEqual(type(s), float, 'test_US_equity LOW {}'.format(s))

        s = financials.getRealtime('NYSE:IBM', Datacode.HIGH.value, 'GOOGLE')
        self.assertEqual(type(s), float, 'test_US_equity HIGH {}'.format(s))

        s = financials.getRealtime('NYSE:IBM', Datacode.LOW_52_WEEK.value, 'GOOGLE')
        self.assertEqual(type(s), float, 'test_US_equity LOW_52_WEEK {}'.format(s))

        s = financials.getRealtime('NYSE:IBM', Datacode.HIGH_52_WEEK.value, 'GOOGLE')
        self.assertEqual(type(s), float, 'test_US_equity HIGH_52_WEEK {}'.format(s))

        s = financials.getRealtime('NYSE:IBM', Datacode.MARKET_CAP.value, 'GOOGLE')
        self.assertEqual(type(s), float, 'test_US_equity MARKET_CAP {}'.format(s))

        # s = financials.getRealtime('NYSE:IBM', Datacode.VOLUME.value, 'GOOGLE')
        # self.assertEqual(type(s), float, 'test_US_equity VOLUME {}'.format(s))

        s = financials.getRealtime('NYSE:IBM', Datacode.TIMESTAMP.value, 'GOOGLE')
        self.assertEqual(s, 'Data doesn\'t exist - 999', 'test_US_equity TIMESTAMP')

        s = financials.getRealtime('NYSE:IBM', Datacode.TIMEZONE.value, 'GOOGLE')
        # self.assertEqual(s, 'America/New_York', 'test_US_equity TIMEZONE')
        self.assertEqual(s, 'GMT-4', 'test_US_equity TIMEZONE')
        # self.assertEqual(s, 'GMT-5', 'test_US_equity TIMEZONE')

    def test_US_mutuals(self):
        s = financials.getRealtime('MUTF:VFIAX', Datacode.LAST_PRICE.value, 'GOOGLE')
        self.assertEqual(type(s), float, 'test_US_mutuals LAST_PRICE - {}'.format(s))

        s = financials.getRealtime('MUTF:VFIAX', Datacode.CURRENCY.value, 'GOOGLE')
        self.assertEqual(s, 'USD', 'test_US_mutuals CURRENCY')

        s = financials.getRealtime('MUTF:VFIAX', Datacode.TIMEZONE.value, 'GOOGLE')
        self.assertEqual(s, 'Data doesn\'t exist - 105', 'test_US_mutuals')

    def test_index(self):
        s = financials.getRealtime('INDEXDB:DAX', Datacode.LAST_PRICE.value, 'GOOGLE')
        self.assertEqual(type(s), float, 'test_index LAST_PRICE {}'.format(s))

        s = financials.getRealtime('INDEXDB:DAX', Datacode.CHANGE_IN_PERCENT.value, 'GOOGLE')
        self.assertEqual(type(s), float, 'test_index CHANGE_IN_PERCENT')

        s = financials.getRealtime('INDEXDB:DAX', Datacode.CHANGE.value, 'GOOGLE')
        self.assertEqual(type(s), float, 'test_index CHANGE')

    def test_errors(self):
        s = financials.getRealtime(None, Datacode.LAST_PRICE.value, 'GOOGLE')
        self.assertEqual(s, 'Ticker is empty', 'test_errors')

        s = financials.getRealtime('NYS:IBM', None, 'GOOGLE')
        self.assertEqual(s, 'Datacode is empty', 'test_errors')

        s = financials.getRealtime('DOES_NOT_EXISTS', Datacode.LAST_PRICE.value, 'GOOGLE')
        self.assertEqual(s, 'Google.getRealtime(DOES_NOT_EXISTS, 21) - no match', 'test_errors')

        s = financials.getRealtime('NYS:IBM', 'Foo', 'GOOGLE')
        self.assertEqual(s, 'Datacode is not a number', 'test_errors')

        # Historic data not supported on GOOGLE

        s = financials.getHistoric('NYS:IBM', Datacode.LAST_PRICE.value, '2017-01-01', 'GOOGLE')
        self.assertEqual(s, 'Source \'GOOGLE\' not supported', 'test_errors')

    def test_errors_cell_range_passed(self):
        cell_range = ((1, 2), ('3', '4'), (5.0, 6.0))

        s = financials.getRealtime(cell_range, Datacode.LAST_PRICE.value, 'GOOGLE')
        self.assertEqual(s, 'Cell range not allowed for ticker', 'test_errors')

        s = financials.getRealtime('NYS:IBM', cell_range, 'GOOGLE')
        self.assertEqual(s, 'Cell range not allowed for datacode', 'test_errors')

        s = financials.getRealtime('NYS:IBM', Datacode.LAST_PRICE.value, cell_range)
        self.assertEqual(s, 'Cell range not allowed for source', 'test_errors')

    def test_support(self):
        cell_range = ((1, 2), ('3', '4'), (5.0, 6.0))

        s = financials.getRealtime('SUPPORT')
        self.assertTrue(s.startswith("ctx="), 'test_errors SUPPORT {}'.format(s))

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
