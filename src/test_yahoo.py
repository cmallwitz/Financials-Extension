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
        s = financials.getRealtime('EURGBP=X', Datacode.CURRENCY.value, 'YAHOO')
        self.assertEqual(str, type(s), 'test_currency CURRENCY')

        s = financials.getRealtime('EURGBP=X', Datacode.LAST_PRICE.value, 'YAHOO')
        self.assertEqual(float, type(s), 'test_currency LAST_PRICE')

    def test_realtime_US_equity(self):

        s = financials.getRealtime('^GSPC', Datacode.NAME.value, 'YAHOO')
        self.assertEqual(str, type(s), 'test_realtime_US_equity NAME {}'.format(s))
        self.assertIn('500', s, 'test_realtime_US_equity NAME {}'.format(s))

        s = financials.getRealtime('IBM', Datacode.PREV_CLOSE.value, 'YAHOO')
        self.assertEqual(float, type(s), 'test_realtime_US_equity PREV_CLOSE {}'.format(s))

        s = financials.getRealtime('IBM', Datacode.OPEN.value, 'YAHOO')
        self.assertEqual(float, type(s), 'test_realtime_US_equity OPEN {}'.format(s))

        s = financials.getRealtime('IBM', Datacode.LAST_PRICE.value, 'YAHOO')
        self.assertEqual(float, type(s), 'test_realtime_US_equity LAST_PRICE {}'.format(s))

        s = financials.getRealtime('IBM', Datacode.LOW.value, 'YAHOO')
        self.assertEqual(float, type(s), 'test_realtime_US_equity LOW {}'.format(s))

        s = financials.getRealtime('IBM', Datacode.HIGH.value, 'YAHOO')
        self.assertEqual(float, type(s), 'test_realtime_US_equity HIGH {}'.format(s))

        s = financials.getRealtime('IBM', Datacode.HIGH_52_WEEK.value, 'YAHOO')
        self.assertEqual(float, type(s), 'test_realtime_US_equity HIGH_52_WEEK {}'.format(s))

        s = financials.getRealtime('IBM', Datacode.LOW_52_WEEK.value, 'YAHOO')
        self.assertEqual(float, type(s), 'test_realtime_US_equity LOW_52_WEEK {}'.format(s))

        s = financials.getRealtime('IBM', Datacode.MARKET_CAP.value, 'YAHOO')
        self.assertEqual(float, type(s), 'test_realtime_US_equity MARKET_CAP {}'.format(s))

        s = financials.getRealtime('IBM', Datacode.VOLUME.value, 'YAHOO')
        self.assertEqual(float, type(s), 'test_realtime_US_equity VOLUME {}'.format(s))

        s = financials.getRealtime('IBM', Datacode.AVG_DAILY_VOL_3MONTH.value, 'YAHOO')
        self.assertEqual(float, type(s), 'test_realtime_US_equity AVG_DAILY_VOL_3MONTH {}'.format(s))

        s = financials.getRealtime('IBM', Datacode.NAME.value, 'YAHOO')
        self.assertEqual(str, type(s), 'test_realtime_US_equity NAME {}'.format(s))
        self.assertEqual(s, 'International Business Machines Corporation',
                         'test_realtime_US_equity NAME {}'.format(s))

        s = financials.getRealtime('IBM', Datacode.SECTOR.value, 'YAHOO')
        self.assertEqual(str, type(s), 'test_realtime_US_equity SECTOR {}'.format(s))
        self.assertEqual(s, 'Technology', 'test_realtime_US_equity SECTOR {}'.format(s))

        s = financials.getRealtime('IBM', Datacode.INDUSTRY.value, 'YAHOO')
        self.assertEqual(str, type(s), 'test_realtime_US_equity INDUSTRY {}'.format(s))
        self.assertEqual(s, 'Information Technology Services', 'test_realtime_US_equity INDUSTRY {}'.format(s))

        s = financials.getRealtime('IBM', Datacode.TIMEZONE.value, 'YAHOO')
        self.assertEqual(s, 'America/New_York', 'test_realtime_US_equity TIMEZONE {}'.format(s))

        s = financials.getRealtime('IBM', Datacode.BETA.value, 'YAHOO')
        self.assertTrue(testutils.is_positive_float(s), 'test_realtime_US_equity BETA {}'.format(s))

        s = financials.getRealtime('IBM', Datacode.EPS.value, 'YAHOO')
        self.assertTrue(testutils.is_positive_float(s), 'test_realtime_US_equity EPS {}'.format(s))

        s = financials.getRealtime('IBM', Datacode.PE_RATIO.value, 'YAHOO')
        self.assertTrue(testutils.is_positive_float(s), 'test_realtime_US_equity PE_RATIO {}'.format(s))

        s = financials.getRealtime('IBM', Datacode.DIV.value, 'YAHOO')
        self.assertTrue(testutils.is_positive_float(s), 'test_realtime_US_equity DIV {}'.format(s))

        s = financials.getRealtime('IBM', Datacode.DIV_YIELD.value, 'YAHOO')
        self.assertTrue(testutils.is_positive_float(s), 'test_realtime_US_equity DIV_YIELD {}'.format(s))

        s = financials.getRealtime('IBM', Datacode.EX_DIV_DATE.value, 'YAHOO')
        self.assertEqual(str, type(s), 'test_realtime_US_equity EX_DIV_DATE {}'.format(s))
        self.assertTrue(testutils.is_date(s), 'test_realtime_US_equity EX_DIV_DATE {}'.format(s))

        s = financials.getRealtime('IBM', Datacode.PAYOUT_RATIO.value, 'YAHOO')
        self.assertTrue(testutils.is_positive_float(s), 'test_realtime_US_equity PAYOUT_RATIO {}'.format(s))

        s = financials.getRealtime('IBM', Datacode.EXCHANGE.value, 'YAHOO')
        self.assertEqual(s, 'NYQ', 'test_realtime_US_equity EXCHANGE')

    def test_realtime_US_mutuals(self):

        s = financials.getRealtime('VGSLX', Datacode.LAST_PRICE.value, 'YAHOO')
        self.assertEqual(float, type(s), 'test_realtime_US_mutuals LAST_PRICE {}'.format(s))

        s = financials.getRealtime('VFIAX', Datacode.LAST_PRICE.value, 'YAHOO')
        self.assertEqual(float, type(s), 'test_realtime_US_mutuals LAST_PRICE {}'.format(s))

        s = financials.getRealtime('VFIAX', Datacode.LAST_PRICE_DATE.value, 'YAHOO')
        self.assertEqual(str, type(s), 'test_realtime_US_mutuals LAST_PRICE_DATE {}'.format(s))

        s = financials.getRealtime('VFIAX', Datacode.LAST_PRICE_TIME.value, 'YAHOO')
        self.assertEqual(str, type(s), 'test_realtime_US_mutuals LAST_PRICE_TIME {}'.format(s))

        s = financials.getRealtime('VFIAX', Datacode.DIV_YIELD.value, 'YAHOO')
        self.assertTrue(testutils.is_positive_float(s), 'test_realtime_US_mutuals DIV_YIELD {}'.format(s))

    def test_realtime_US_options(self):

        # symbol from https://finance.yahoo.com/quote/IBM/options?p=IBM
        
        s = financials.getRealtime('IBM230120C00130000', Datacode.PREV_CLOSE.value, 'YAHOO')
        self.assertEqual(float, type(s), 'test_realtime_US_options PREV_CLOSE {}'.format(s))

        s = financials.getRealtime('IBM230120C00130000', Datacode.NAME.value, 'YAHOO')
        self.assertEqual(str, type(s), 'test_realtime_US_options NAME {}'.format(s))
        self.assertEqual('IBM Jan 2023 130.000 call', s, 'test_realtime_US_options NAME {}'.format(s))

        s = financials.getRealtime('IBM230120C00130000', Datacode.EXPIRY_DATE.value, 'YAHOO')
        self.assertEqual(str, type(s), 'test_realtime_US_options EXPIRY_DATE {}'.format(s))
        self.assertTrue(testutils.is_date(s), 'test_realtime_US_options EXPIRY_DATE {}'.format(s))
        self.assertEqual("2023-01-20", s, 'test_realtime_US_options EXPIRY_DATE {}'.format(s))

        s = financials.getRealtime('IBM230120C00130000', Datacode.LAST_PRICE.value, 'YAHOO')
        self.assertEqual(float, type(s), 'test_realtime_US_options LAST_PRICE {}'.format(s))

        s = financials.getRealtime('IBM230120C00130000', Datacode.OPEN.value, 'YAHOO')
        self.assertEqual(float, type(s), 'test_realtime_US_options OPEN {}'.format(s))

        s = financials.getRealtime('IBM230120C00130000', Datacode.VOLUME.value, 'YAHOO')
        self.assertEqual(float, type(s), 'test_realtime_US_options VOLUME {}'.format(s))

        s = financials.getRealtime('IBM230120C00130000', Datacode.BID.value, 'YAHOO')
        self.assertEqual(float, type(s), 'test_realtime_US_options BID {}'.format(s))

        s = financials.getRealtime('IBM230120C00130000', Datacode.ASK.value, 'YAHOO')
        self.assertEqual(float, type(s), 'test_realtime_US_options ASK {}'.format(s))

        s = financials.getRealtime('IBM230120C00130000', Datacode.BIDSIZE.value, 'YAHOO')
        self.assertEqual(float, type(s), 'test_realtime_US_options BIDSIZE {}'.format(s))

        s = financials.getRealtime('IBM230120C00130000', Datacode.ASKSIZE.value, 'YAHOO')
        self.assertEqual(float, type(s), 'test_realtime_US_options ASKSIZE {}'.format(s))

    def test_realtime_UK_ETF(self):

        s = financials.getRealtime('VERX.L', Datacode.LAST_PRICE.value, 'YAHOO')
        self.assertEqual(float, type(s), 'test_realtime_UK_ETF LAST_PRICE {}'.format(s))

        s = financials.getRealtime('VERX.L', Datacode.TIMEZONE.value, 'YAHOO')
        self.assertEqual(s, 'Europe/London', 'test_realtime_UK_ETF TIMEZONE {}'.format(s))

        s = financials.getRealtime('CSP1.L', Datacode.NAME.value, 'YAHOO')
        self.assertEqual(str, type(s), 'test_realtime_UK_ETF NAME {}'.format(s))
        self.assertEqual(s, 'iShares VII Public Limited Company - iShares Core S&P 500 UCITS ETF',
                         'test_realtime_UK_ETF NAME {}'.format(s))

    def test_realtime_DE_equity(self):

        s = financials.getRealtime('SAP.DE', Datacode.LAST_PRICE.value, 'YAHOO')
        self.assertEqual(float, type(s), 'test_realtime_DE_equity LAST_PRICE {}'.format(s))

        s = financials.getRealtime('SAP.DE', Datacode.TIMEZONE.value, 'YAHOO')
        self.assertEqual(s, 'Europe/Berlin', 'test_realtime_DE_equity TIMEZONE {}'.format(s))

        s = financials.getRealtime('SAP.DE', Datacode.SECTOR.value, 'YAHOO')
        self.assertEqual(str, type(s), 'test_realtime_DE_equity SECTOR {}'.format(s))
        self.assertEqual(s, 'Technology', 'test_realtime_DE_equity SECTOR {}'.format(s))

        s = financials.getRealtime('SAP.DE', Datacode.INDUSTRY.value, 'YAHOO')
        self.assertEqual(str, type(s), 'test_realtime_DE_equity INDUSTRY {}'.format(s))
        self.assertEqual(s, 'Software—Application', 'test_realtime_DE_equity INDUSTRY {}'.format(s))

        s = financials.getRealtime('C060.DE', Datacode.NAME.value, 'YAHOO')
        self.assertEqual(str, type(s), 'test_realtime_DE_equity NAME {}'.format(s))

        s = financials.getRealtime('C060.DE', Datacode.EXCHANGE.value, 'YAHOO')
        self.assertEqual(s, 'GER', 'test_realtime_DE_equity EXCHANGE')

    def test_DK_equity(self):
        s = financials.getRealtime('NOVO-B.CO', 'name', 'YAHOO')
        self.assertEqual('Novo Nordisk A/S', s, 'test_DK_equity NAME {}'.format(s))

        s = financials.getRealtime('NOVO-B.CO', 'currency', 'YAHOO')
        self.assertEqual('DKK', s, 'test_DK_equity CURRENCY {}'.format(s))

        s = financials.getRealtime('NOVO-B.CO', 'industry', 'YAHOO')
        self.assertEqual(str, type(s), 'test_DK_equity INDUSTRY {}'.format(s))
        self.assertEqual('Biotechnology', s, 'test_DK_equity INDUSTRY {}'.format(s))

    def test_realtime_TY_equity(self):
        s = financials.getRealtime('6503.T', Datacode.OPEN.value, 'YAHOO')
        self.assertEqual(float, type(s), 'test_TY_equity OPEN {}'.format(s))

        s = financials.getRealtime('6503.T', Datacode.LOW.value, 'YAHOO')
        self.assertEqual(float, type(s), 'test_TY_equity LOW {}'.format(s))

        s = financials.getRealtime('6503.T', Datacode.HIGH.value, 'YAHOO')
        self.assertEqual(float, type(s), 'test_TY_equity HIGH {}'.format(s))

        s = financials.getRealtime('6503.T', Datacode.LOW_52_WEEK.value, 'YAHOO')
        self.assertEqual(float, type(s), 'test_TY_equity LOW_52_WEEK {}'.format(s))

        s = financials.getRealtime('6503.T', Datacode.HIGH_52_WEEK.value, 'YAHOO')
        self.assertEqual(float, type(s), 'test_TY_equity HIGH_52_WEEK {}'.format(s))

        s = financials.getRealtime('6503.T', Datacode.MARKET_CAP.value, 'YAHOO')
        self.assertEqual(float, type(s), 'test_TY_equity MARKET_CAP {}'.format(s))

        s = financials.getRealtime('6503.T', Datacode.VOLUME.value, 'YAHOO')
        self.assertEqual(float, type(s), 'test_TY_equity VOLUME {}'.format(s))

        s = financials.getRealtime('6503.T', Datacode.CURRENCY.value, 'YAHOO')
        self.assertEqual(s, 'JPY', 'test_TY_equity CURRENCY')

        s = financials.getRealtime('6503.T', Datacode.SECTOR.value, 'YAHOO')
        self.assertEqual(str, type(s), 'test_TY_equity SECTOR {}'.format(s))
        self.assertEqual(s, 'Industrials', 'test_TY_equity SECTOR {}'.format(s))

        s = financials.getRealtime('6503.T', Datacode.INDUSTRY.value, 'YAHOO')
        self.assertEqual(str, type(s), 'test_TY_equity INDUSTRY {}'.format(s))
        self.assertEqual(s, 'Electrical Equipment & Parts', 'test_TY_equity INDUSTRY {}'.format(s))

    def test_historic_US_equity(self):

        s = financials.getHistoric('IBM', Datacode.LAST_PRICE.value, '2017-01-01', 'YAHOO')
        self.assertEqual('Not a trading day \'2017-01-01\'', s, 'test_historic_US_equity LAST_PRICE {}'.format(s))

        s = financials.getHistoric('IBM', Datacode.CLOSE.value, '2017-01-01', 'YAHOO')
        self.assertEqual('Not a trading day \'2017-01-01\'', s, 'test_historic_US_equity CLOSE {}'.format(s))

        s = financials.getHistoric('IBM', Datacode.LAST_PRICE.value, '2017-01-03', 'YAHOO')
        self.assertIsNone(s, 'test_historic_US_equity LAST_PRICE {}'.format(s))

        s = financials.getHistoric('IBM', Datacode.CLOSE.value, '2017-01-03', 'YAHOO')
        self.assertEqual(167.190002, s, 'test_historic_US_equity CLOSE {}'.format(s))

        financials.yahoo.historicdata = {}

        s = financials.getHistoric('IBM', Datacode.CLOSE.value, '2017-01-03', 'YAHOO')
        self.assertEqual(167.190002, s, 'test_historic_US_equity CLOSE {}'.format(s))

        directory = os.path.join(str(pathlib.Path.home()), '.financials-extension')
        ibm = os.path.join(directory, 'yahoo-IBM.csv')
        try:
            os.unlink(ibm)
        except:
            pass  # ignore if file doesn't exists

        financials.yahoo.historicdata = {}

        s = financials.getHistoric('IBM', Datacode.CLOSE.value, '2017-01-03', 'YAHOO')
        self.assertEqual(167.190002, s, 'test_historic_US_equity CLOSE {}'.format(s))

        # Note: quarterly dividend and splits will change past adjusted prices - will fail after the next dividend
        s = financials.getHistoric('IBM', Datacode.ADJ_CLOSE.value, '2017-01-03', 'YAHOO')
        self.assertEqual(136.249847, s, 'test_historic_US_equity ADJ_CLOSE {}'.format(s))

    def test_historic_UK_ETF(self):

        directory = os.path.join(str(pathlib.Path.home()), '.financials-extension')
        verx = os.path.join(directory, 'yahoo-VERX.L.csv')
        try:
            os.unlink(verx)
        except:
            pass  # ignore if file doesn't exists

        financials.yahoo.historicdata = {}

        s = financials.getHistoric('VERX.L', Datacode.LAST_PRICE.value, '2017-01-01', 'YAHOO')
        self.assertEqual(s, 'Not a trading day \'2017-01-01\'', 'test_historic_UK_ETF LAST_PRICE {}'.format(s))

        s = financials.getHistoric('VERX.L', Datacode.CLOSE.value, '2017-01-03', 'YAHOO')
        self.assertEqual(s, 23.24, 'test_historic_UK_ETF CLOSE {}'.format(s))

        s = financials.getHistoric('VERX.L', Datacode.CLOSE.value, '2016-10-03', 'YAHOO')
        self.assertEqual(s, 22.26, 'test_historic_UK_ETF CLOSE {}'.format(s))

        #  Inception Date 2014-09-30
        s = financials.getHistoric('VERX.L', Datacode.CLOSE.value, '2018-04-02', 'YAHOO')
        self.assertEqual(s, 'Not a trading day \'2018-04-02\'', 'test_historic_UK_ETF CLOSE {}'.format(s))

        #  Inception Date 2014-09-30
        s = financials.getHistoric('VERX.L', Datacode.CLOSE.value, '2015-01-01', 'YAHOO')
        self.assertEqual(s, 'Not a trading day \'2015-01-01\'', 'test_historic_UK_ETF CLOSE {}'.format(s))

        s = financials.getHistoric('VERX.L', Datacode.CLOSE.value, 42738, 'YAHOO')  # 2017-01-03
        self.assertEqual(s, 23.24, 'test_historic_UK_ETF CLOSE {}'.format(s))

        s = financials.getHistoric('VERX.L', Datacode.CLOSE.value, 42738.0, 'YAHOO')  # 2017-01-03
        self.assertEqual(s, 23.24, 'test_historic_UK_ETF CLOSE {}'.format(s))

        s = financials.getHistoric('VERX.L', Datacode.CLOSE.value, 42646.0, 'YAHOO')  # 2016-10-03
        self.assertEqual(s, 22.26, 'test_historic_UK_ETF CLOSE {}'.format(s))

    def test_historic_DE_equity(self):

        s = financials.getHistoric('SAP.DE', Datacode.LAST_PRICE.value, '2017-01-01', 'YAHOO')
        self.assertEqual(s, 'Not a trading day \'2017-01-01\'', 'test_historic_DE_equity LAST_PRICE {}'.format(s))

        s = financials.getHistoric('SAP.DE', Datacode.CLOSE.value, '2017-01-03', 'YAHOO')
        self.assertEqual(s, 82.889999, 'test_historic_DE_equity CLOSE {}'.format(s))

        s = financials.getHistoric('C060.DE', Datacode.CLOSE.value, '2017-01-03', 'YAHOO')
        self.assertEqual(s, 68.209999, 'test_historic_DE_equity CLOSE {}'.format(s))

    def test_realtime_errors(self):

        s = financials.getRealtime('NO_NAME', Datacode.LAST_PRICE.value, 'YAHOO')
        self.assertIsNone(s, 'test_realtime_errors LAST_PRICE {}'.format(s))

        s = financials.getRealtime('C060.DE', -1, 'YAHOO')
        self.assertEqual('Datacode -1 not supported', s, 'test_realtime_errors -1 {}'.format(s))

    def test_historic_errors(self):

        s = financials.getHistoric('NO_NAME', Datacode.LAST_PRICE.value, '2018-01-08', 'YAHOO')
        self.assertIsNone(s, 'test_historic_errors LAST_PRICE {}'.format(s))

        s = financials.getHistoric('IBM', Datacode.CLOSE.value, '2030-01-01', 'YAHOO')
        self.assertEqual(s, 'Future date \'2030-01-01\'', 'test_historic_errors CLOSE {}'.format(s))

        s = financials.getRealtime('IBM', 9999, 'YAHOO')
        self.assertEqual(s, 'Datacode 9999 not supported', 'test_historic_errors 9999')

        s = financials.getRealtime('IBM', Datacode.ADJ_CLOSE.value, 'YAHOO')
        self.assertIsNone(s, 'test_historic_errors ADJ_CLOSE {}'.format(s))

        s = financials.getHistoric('IBM', Datacode.CLOSE.value, '2030-01-01', 'YAHOO')
        self.assertEqual(s, 'Future date \'2030-01-01\'', 'test_historic_errors CLOSE {}'.format(s))

        s = financials.getHistoric('IBM', Datacode.CLOSE.value, '1990-01-01', 'YAHOO')
        self.assertEqual(s, 'Date before 2000 \'1990-01-01\'', 'test_historic_errors CLOSE {}'.format(s))

        s = financials.getHistoric('IBM', Datacode.CLOSE.value, 'abcdef', 'YAHOO')
        self.assertEqual(s, 'Date format not supported: \'abcdef\'', 'test_historic_errors CLOSE {}'.format(s))

        s = financials.getHistoric('IBM', Datacode.CLOSE.value, True, 'YAHOO')
        self.assertEqual(s, 'Date type not supported: <class \'bool\'> \'True\'',
                         'test_historic_errors CLOSE {}'.format(s))

        s = financials.getHistoric('IBM', Datacode.CLOSE.value, -1000000, 'YAHOO')
        self.assertEqual(s, 'Date format not supported: -1000000', 'test_historic_errors CLOSE {}'.format(s))

    def test_errors_cell_range_passed(self):
        cell_range = ((1, 2), ('3', '4'), (5.0, 6.0))

        s = financials.getHistoric(cell_range, Datacode.CLOSE.value, '2017-01-03', 'YAHOO')
        self.assertEqual(s, 'Cell range not allowed for ticker', 'test_errors')

        s = financials.getHistoric('IBM', cell_range, '2017-01-03', 'YAHOO')
        self.assertEqual(s, 'Cell range not allowed for datacode', 'test_errors')

        s = financials.getHistoric('IBM', Datacode.CLOSE.value, cell_range, 'YAHOO')
        self.assertEqual(s, 'Cell range not allowed for date', 'test_errors')

        s = financials.getHistoric('IBM', Datacode.CLOSE.value, '2017-01-03', cell_range)
        self.assertEqual(s, 'Cell range not allowed for source', 'test_errors')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('unittest_args', nargs='*')
    args = parser.parse_args()
    unit_argv = [sys.argv[0]] + args.unittest_args
    unittest.main(argv=unit_argv)
