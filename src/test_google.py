#  test_google.py
#
#  license: GNU LGPL
#
#  This library is free software; you can redistribute it and/or
#  modify it under the terms of the GNU Lesser General Public
#  License as published by the Free Software Foundation; either
#  version 3 of the License, or (at your option) any later version.

import unittest

import financials
from datacode import Datacode

financials = financials.createInstance(None)


class TestGoogle(unittest.TestCase):

    def test_currency(self):
        s = financials.getRealtime('EURGBP', Datacode.LAST_PRICE.value, 'GOOGLE')
        self.assertEqual(type(s), float, 'test_currency LAST_PRICE')

        s = financials.getRealtime('EURGBP', Datacode.CURRENCY.value, 'GOOGLE')
        self.assertEqual(type(s), str, 'test_currency CURRENCY')
        self.assertEqual(s, '', 'test_currency CURRENCY')

    def test_UK_equity(self):
        s = financials.getRealtime('EURGBP', Datacode.LAST_PRICE.value, 'GOOGLE')
        self.assertEqual(type(s), float, 'test_UK_equity LAST_PRICE')

        s = financials.getRealtime('LON:VOD', Datacode.LAST_PRICE.value, 'GOOGLE')
        self.assertEqual(type(s), float, 'test_UK_equity LAST_PRICE')

        s = financials.getRealtime('VOD.L', Datacode.LAST_PRICE.value, 'GOOGLE')
        self.assertEqual(type(s), float, 'test_UK_equity LAST_PRICE')

        s = financials.getRealtime('VOD.L', Datacode.TICKER.value, 'GOOGLE')
        self.assertEqual(s, 'VOD', 'test_UK_equity TICKER')

        s = financials.getRealtime('VOD.L', Datacode.NAME.value, 'GOOGLE')
        self.assertEqual(type(s), str, 'test_UK_equity NAME')

    def test_UK_ETF(self):
        s = financials.getRealtime('LON:CSP1', Datacode.LAST_PRICE.value, 'GOOGLE')
        self.assertEqual(type(s), float, 'test_UK_ETF LAST_PRICE')

        s = financials.getRealtime('LON:CSP1', Datacode.CURRENCY.value, 'GOOGLE')
        self.assertEqual(s, 'GBX', 'test_UK_ETF CURRENCY')

        s = financials.getRealtime('LON:FTAL', Datacode.LAST_PRICE.value, 'GOOGLE')
        self.assertEqual(type(s), float, 'test_UK_ETF LAST_PRICE')

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
        self.assertEqual(s, 'Europe/Berlin', 'test_DE_equity TIMEZONE')

    def test_DE_ETF(self):
        s = financials.getRealtime('FRA:C060', Datacode.LAST_PRICE.value, 'GOOGLE')
        self.assertEqual(type(s), float, 'test_DE_ETF LAST_PRICE')

        s = financials.getRealtime('FRA:C060', Datacode.CURRENCY.value, 'GOOGLE')
        self.assertEqual(s, 'EUR', 'test_DE_ETF CURRENCY')

        s = financials.getRealtime('C060.de', Datacode.LAST_PRICE.value, 'GOOGLE')
        self.assertEqual(type(s), float, 'test_DE_ETF LAST_PRICE')

        s = financials.getRealtime('C060.de', Datacode.TICKER.value, 'GOOGLE')
        self.assertEqual(s, 'C060', 'test_DE_ETF CURRENCY')

        s = financials.getRealtime('C060.de', Datacode.EXCHANGE.value, 'GOOGLE')
        self.assertEqual(s, 'FRA', 'test_DE_ETF CURRENCY')

        s = financials.getRealtime('C060.de', Datacode.CURRENCY.value, 'GOOGLE')
        self.assertEqual(s, 'EUR', 'test_DE_ETF CURRENCY')

    def test_US_equity(self):
        s = financials.getRealtime(' NASDAQ : AAPL ', Datacode.LAST_PRICE.value, 'GOOGLE')
        self.assertEqual(type(s), float, 'test_US_equity LAST_PRICE')

        s = financials.getRealtime(' NASDAQ : AAPL ', Datacode.TICKER.value, 'GOOGLE')
        self.assertEqual(s, 'AAPL', 'test_US_equity TICKER')

        s = financials.getRealtime(' NASDAQ : AAPL ', Datacode.EXCHANGE.value, 'GOOGLE')
        self.assertEqual(s, 'NASDAQ', 'test_US_equity EXCHANGE')

        s = financials.getRealtime(' NASDAQ : AAPL ', Datacode.CURRENCY.value, 'GOOGLE')
        self.assertEqual(s, 'USD', 'test_US_equity CURRENCY')

        s = financials.getRealtime('NYSE:IBM', Datacode.LAST_PRICE.value, 'GOOGLE')
        self.assertEqual(type(s), float, 'test_US_equity LAST_PRICE')

        s = financials.getRealtime('NYSE:IBM', Datacode.TICKER.value, 'GOOGLE')
        self.assertEqual(s, 'IBM', 'test_US_equity TICKER')

        s = financials.getRealtime('NYSE:IBM', Datacode.EXCHANGE.value, 'GOOGLE')
        self.assertEqual(s, 'NYSE', 'test_US_equity EXCHANGE')

        s = financials.getRealtime('NYSE:IBM', Datacode.CURRENCY.value, 'GOOGLE')
        self.assertEqual(s, 'USD', 'test_US_equity CURRENCY')

        s = financials.getRealtime('NYSE:IBM', Datacode.NAME.value, 'GOOGLE')
        self.assertEqual(type(s), str, 'test_US_equity NAME')

        s = financials.getRealtime('NYSE:IBM', Datacode.NAME.value, 'GOOGLE')
        self.assertEqual(type(s), str, 'test_US_equity NAME')

        s = financials.getRealtime('NYSE:IBM', Datacode.TIMESTAMP.value, 'GOOGLE')
        self.assertEqual(s, 'Data doesn\'t exist - 999', 'test_US_equity TIMESTAMP')

        s = financials.getRealtime('NYSE:IBM', Datacode.TIMEZONE.value, 'GOOGLE')
        self.assertEqual(s, 'America/New_York', 'test_US_equity TIMEZONE')

    def test_US_mutuals(self):
        s = financials.getRealtime('MUTF:VFIAX', Datacode.LAST_PRICE.value, 'GOOGLE')
        self.assertEqual(type(s), float, 'test_US_mutuals LAST_PRICE')

        s = financials.getRealtime('MUTF:VFIAX', Datacode.CURRENCY.value, 'GOOGLE')
        self.assertEqual(s, 'USD', 'test_US_mutuals CURRENCY')

    def test_errors(self):
        s = financials.getRealtime(None, Datacode.LAST_PRICE.value, 'GOOGLE')
        self.assertEqual(s, 'Ticker is empty', 'test_errors')

        s = financials.getRealtime('NYS:IBM', None, 'GOOGLE')
        self.assertEqual(s, 'Datacode is empty', 'test_errors')

        s = financials.getRealtime('DOES_NOT_EXISTS', Datacode.LAST_PRICE.value, 'GOOGLE')
        self.assertEqual(s, 'Data for \'DOES_NOT_EXISTS\' not found', 'test_errors')

        s = financials.getRealtime('NYS:IBM', 'Foo', 'GOOGLE')
        self.assertEqual(s, 'Datacode is not a number', 'test_errors')

        # Historic data not supported on GOOGLE

        s = financials.getHistoric('NYS:IBM', Datacode.LAST_PRICE.value, '2017-01-01', 'GOOGLE')
        self.assertEqual(s, 'getHistoric: Source \'GOOGLE\' not supported', 'test_errors')

    def test_errors_cell_range_passed(self):
        range = ((1, 2),('3', '4'),(5.0, 6.0))

        s = financials.getRealtime(range, Datacode.LAST_PRICE.value, 'GOOGLE')
        self.assertEqual(s, 'Cell range not allowed for ticker', 'test_errors')

        s = financials.getRealtime('NYS:IBM', range, 'GOOGLE')
        self.assertEqual(s, 'Cell range not allowed for datacode', 'test_errors')

        s = financials.getRealtime('NYS:IBM', Datacode.LAST_PRICE.value, range)
        self.assertEqual(s, 'Cell range not allowed for source', 'test_errors')

    def test_support(self):
        range = ((1, 2), ('3', '4'), (5.0, 6.0))

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

        s = financials.getRealtime('SUPPORT', range)
        self.assertTrue(s.startswith("ctx="), 'test_errors SUPPORT {}'.format(s))
        self.assertTrue("type(datacode)=<class 'tuple'>" in s, 'test_errors SUPPORT {}'.format(s))
        self.assertTrue("str(datacode)=((1, 2), ('3', '4'), (5.0, 6.0))" in s, 'test_errors SUPPORT {}'.format(s))


if __name__ == '__main__':
    unittest.main()
