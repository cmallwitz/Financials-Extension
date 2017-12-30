#  test_yahoo.py
#
#  license: GNU LGPL
#
#  This library is free software; you can redistribute it and/or
#  modify it under the terms of the GNU Lesser General Public
#  License as published by the Free Software Foundation; either
#  version 3 of the License, or (at your option) any later version.

import os
import pathlib
import unittest

import financials
from datacode import Datacode

financials = financials.createInstance(None)


class TestYahoo(unittest.TestCase):

    def test_realtime_US_equity(self):

        s = financials.getRealtime('IBM', Datacode.PREV_CLOSE.value, 'YAHOO')
        self.assertEqual(type(s), float, 'test_realtime_US_equity PREV_CLOSE {}'.format(s))

        s = financials.getRealtime('IBM', Datacode.OPEN.value, 'YAHOO')
        self.assertEqual(type(s), float, 'test_realtime_US_equity OPEN {}'.format(s))

        s = financials.getRealtime('IBM', Datacode.LAST_PRICE.value, 'YAHOO')
        self.assertEqual(type(s), float, 'test_realtime_US_equity LAST_PRICE {}'.format(s))

        s = financials.getRealtime('IBM', Datacode.LOW.value, 'YAHOO')
        self.assertEqual(type(s), float, 'test_realtime_US_equity LOW {}'.format(s))

        s = financials.getRealtime('IBM', Datacode.HIGH.value, 'YAHOO')
        self.assertEqual(type(s), float, 'test_realtime_US_equity HIGH {}'.format(s))

        s = financials.getRealtime('IBM', Datacode.VOLUME.value, 'YAHOO')
        self.assertEqual(type(s), float, 'test_realtime_US_equity VOLUME {}'.format(s))

        s = financials.getRealtime('IBM', Datacode.AVG_DAILY_VOL_3MOMTH.value, 'YAHOO')
        self.assertEqual(type(s), float, 'test_realtime_US_equity AVG_DAILY_VOL_3MOMTH {}'.format(s))

        s = financials.getRealtime('IBM', Datacode.NAME.value, 'YAHOO')
        self.assertEqual(type(s), str, 'test_realtime_US_equity NAME {}'.format(s))

        s = financials.getRealtime('IBM', Datacode.TIMEZONE.value, 'YAHOO')
        self.assertEqual(s, 'America/New_York', 'test_realtime_US_equity TIMEZONE {}'.format(s))

    def test_realtime_UK_ETF(self):

        s = financials.getRealtime('VERX.L', Datacode.LAST_PRICE.value, 'YAHOO')
        self.assertEqual(type(s), float, 'test_realtime_UK_ETF LAST_PRICE {}'.format(s))

        s = financials.getRealtime('VERX.L', Datacode.TIMEZONE.value, 'YAHOO')
        self.assertEqual(s, 'Europe/London', 'test_realtime_UK_ETF TIMEZONE {}'.format(s))

    def test_realtime_DE_equity(self):

        s = financials.getRealtime('SAP.DE', Datacode.LAST_PRICE.value, 'YAHOO')
        self.assertEqual(type(s), float, 'test_realtime_DE_equity LAST_PRICE {}'.format(s))

        s = financials.getRealtime('SAP.DE', Datacode.TIMEZONE.value, 'YAHOO')
        self.assertEqual(s, 'Europe/Berlin', 'test_realtime_DE_equity TIMEZONE {}'.format(s))

    def test_historic_US_equity(self):

        s = financials.getHistoric('IBM', Datacode.LAST_PRICE.value, '2017-01-01', 'YAHOO')
        self.assertEqual(s, 'Not a trading day \'2017-01-01\'', 'test_historic_US_equity LAST_PRICE {}'.format(s))

        s = financials.getHistoric('IBM', Datacode.CLOSE.value, '2017-01-01', 'YAHOO')
        self.assertEqual(s, 'Not a trading day \'2017-01-01\'', 'test_historic_US_equity CLOSE {}'.format(s))

        s = financials.getHistoric('IBM', Datacode.LAST_PRICE.value, '2017-01-03', 'YAHOO')
        self.assertEqual(s, 'Data doesn\'t exist - 21', 'test_historic_US_equity LAST_PRICE {}'.format(s))

        s = financials.getHistoric('IBM', Datacode.CLOSE.value, '2017-01-03', 'YAHOO')
        self.assertEqual(s, 167.190002, 'test_historic_US_equity CLOSE {}'.format(s))

        financials.yahoo.historicdata = {}

        s = financials.getHistoric('IBM', Datacode.CLOSE.value, '2017-01-03', 'YAHOO')
        self.assertEqual(s, 167.190002, 'test_historic_US_equity CLOSE {}'.format(s))

        dir = os.path.join(str(pathlib.Path.home()), '.financials-extension')
        ibm = os.path.join(dir, 'yahoo-IBM.csv')
        try:
            os.unlink(ibm)
        except:
            pass # ignore if file doesn't exists

        financials.yahoo.historicdata = {}

        s = financials.getHistoric('IBM', Datacode.CLOSE.value, '2017-01-03', 'YAHOO')
        self.assertEqual(s, 167.190002, 'test_historic_US_equity CLOSE {}'.format(s))

        s = financials.getHistoric('IBM', Datacode.ADJ_CLOSE.value, '2017-01-03', 'YAHOO')
        self.assertEqual(s, 160.947433, 'test_historic_US_equity ADJ_CLOSE {}'.format(s))

    def test_historic_UK_ETF(self):

        dir = os.path.join(str(pathlib.Path.home()), '.financials-extension')
        verx = os.path.join(dir, 'yahoo-VERX.L.csv')
        try:
            os.unlink(verx)
        except:
            pass # ignore if file doesn't exists

        financials.yahoo.historicdata = {}

        # Inception Date 2014-09-30
        s = financials.getHistoric('VERX.L', Datacode.CLOSE.value, '2014-01-06', 'YAHOO')
        self.assertEqual(s, 'Not a trading day \'2014-01-06\'', 'test_historic_UK_ETF CLOSE {}'.format(s))

        s = financials.getHistoric('VERX.L', Datacode.LAST_PRICE.value, '2017-01-01', 'YAHOO')
        self.assertEqual(s, 'Not a trading day \'2017-01-01\'', 'test_historic_UK_ETF LAST_PRICE {}'.format(s))

        s = financials.getHistoric('VERX.L', Datacode.CLOSE.value, '2017-01-03', 'YAHOO')
        self.assertEqual(s, 23.24, 'test_historic_UK_ETF CLOSE {}'.format(s))

        s = financials.getHistoric('VERX.L', Datacode.CLOSE.value, '2016-10-03', 'YAHOO')
        self.assertEqual(s, 22.26, 'test_historic_UK_ETF CLOSE {}'.format(s))

        # Inception Date 2014-09-30
        s = financials.getHistoric('VERX.L', Datacode.CLOSE.value, '2014-01-06', 'YAHOO')
        self.assertEqual(s, 'Not a trading day \'2014-01-06\'', 'test_historic_UK_ETF CLOSE {}'.format(s))

        s = financials.getHistoric('VERX.L', Datacode.CLOSE.value, 42738, 'YAHOO') # 2017-01-03
        self.assertEqual(s, 23.24, 'test_historic_UK_ETF CLOSE {}'.format(s))

        s = financials.getHistoric('VERX.L', Datacode.CLOSE.value, 42738.0, 'YAHOO') # 2017-01-03
        self.assertEqual(s, 23.24, 'test_historic_UK_ETF CLOSE {}'.format(s))

        s = financials.getHistoric('VERX.L', Datacode.CLOSE.value, 42646.0, 'YAHOO') # 2016-10-03
        self.assertEqual(s, 22.26, 'test_historic_UK_ETF CLOSE {}'.format(s))

    def test_historic_DE_equity(self):

        s = financials.getHistoric('SAP.DE', Datacode.LAST_PRICE.value, '2017-01-01', 'YAHOO')
        self.assertEqual(s, 'Not a trading day \'2017-01-01\'', 'test_historic_DE_equity LAST_PRICE {}'.format(s))

        s = financials.getHistoric('SAP.DE', Datacode.CLOSE.value, '2017-01-03', 'YAHOO')
        self.assertEqual(s, 82.889999, 'test_historic_DE_equity CLOSE {}'.format(s))

        s = financials.getHistoric('C060.DE', Datacode.CLOSE.value, '2017-01-03', 'YAHOO')
        self.assertEqual(s, 72.870003, 'test_historic_DE_equity CLOSE {}'.format(s))

    def test_errors(self):

        s = financials.getRealtime('IBM', 9999, 'YAHOO')
        self.assertEqual(s, 'Datacode 9999 not supported', 'test_errors 9999')

        s = financials.getRealtime('IBM', Datacode.ADJ_CLOSE.value, 'YAHOO')
        self.assertEqual(s, 'Data doesn\'t exist - 91', 'test_errors ADJ_CLOSE {}'.format(s))

        s = financials.getHistoric('IBM', Datacode.CLOSE.value, '2030-01-01', 'YAHOO')
        self.assertEqual(s, 'Future date \'2030-01-01\'', 'test_errors CLOSE {}'.format(s))

        s = financials.getHistoric('IBM', Datacode.CLOSE.value, '1990-01-01', 'YAHOO')
        self.assertEqual(s, 'Date before 2000 \'1990-01-01\'', 'test_errors CLOSE {}'.format(s))

        s = financials.getHistoric('IBM', Datacode.CLOSE.value, 'abcdef', 'YAHOO')
        self.assertEqual(s, 'Date format not supported: \'abcdef\'', 'test_errors CLOSE {}'.format(s))

        s = financials.getHistoric('IBM', Datacode.CLOSE.value, True, 'YAHOO')
        self.assertEqual(s, 'Date type not supported: <class \'bool\'> \'True\'', 'test_errors CLOSE {}'.format(s))

        s = financials.getHistoric('IBM', Datacode.CLOSE.value, -1000000, 'YAHOO')
        self.assertEqual(s, 'Date format not supported: -1000000', 'test_errors CLOSE {}'.format(s))

    def test_errors_cell_range_passed(self):
        range = ((1, 2),('3', '4'),(5.0, 6.0))

        s = financials.getHistoric(range, Datacode.CLOSE.value, '2017-01-03', 'YAHOO')
        self.assertEqual(s, 'Cell range not allowed for ticker', 'test_errors')

        s = financials.getHistoric('IBM', range, '2017-01-03', 'YAHOO')
        self.assertEqual(s, 'Cell range not allowed for datacode', 'test_errors')

        s = financials.getHistoric('IBM', Datacode.CLOSE.value, range, 'YAHOO')
        self.assertEqual(s, 'Cell range not allowed for date', 'test_errors')

        s = financials.getHistoric('IBM', Datacode.CLOSE.value, '2017-01-03', range)
        self.assertEqual(s, 'Cell range not allowed for source', 'test_errors')


if __name__ == '__main__':
    unittest.main()
