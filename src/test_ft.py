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

logging.basicConfig(level=logging.ERROR, format="%(asctime)s %(name)s %(levelname)s %(message)s")

import financials
from datacode import Datacode
import testutils

financials = financials.createInstance(None)


class Test(unittest.TestCase):

    def test_currency(self):
        s = financials.getRealtime('EURGBP', 'LAST_PRICE', 'FT')
        self.assertEqual(float, type(s), 'test_currency LAST_PRICE')

        s = financials.getRealtime('EURGBP', 'CURRENCY', 'FT')
        self.assertEqual(str, type(s), 'test_currency CURRENCY')

    def test_US_equity(self):
        s = financials.getRealtime('INTC:NSQ', 'CHANGE', 'FT')
        self.assertEqual(float, type(s), 'test_US_equity CHANGE {}'.format(s))

        s = financials.getRealtime('INTC:NSQ', 'CHANGE_IN_PERCENT', 'FT')
        self.assertEqual(float, type(s), 'test_US_equity CHANGE_IN_PERCENT {}'.format(s))

        s = financials.getRealtime('INTC:NSQ', 'AVG_DAILY_VOL_3MONTH', 'FT')
        self.assertEqual(float, type(s), 'test_US_equity AVG_DAILY_VOL_3MONTH {}'.format(s))

        s = financials.getRealtime('INTC:NSQ', 'MARKET_CAP', 'FT')
        self.assertEqual(float, type(s), 'test_US_equity MARKET_CAP {}'.format(s))

        s = financials.getRealtime('IBM:NYQ', 'TICKER', 'FT')
        self.assertEqual(str, type(s), 'test_US_equity TICKER {}'.format(s))
        self.assertEqual('IBM:NYQ', s, 'test_US_equity TICKER {}'.format(s))

        s = financials.getRealtime('IBM:NYQ', 'PREV_CLOSE', 'FT')
        self.assertEqual(float, type(s), 'test_US_equity PREV_CLOSE {}'.format(s))

        s = financials.getRealtime('IBM:NYQ', 'OPEN', 'FT')
        self.assertEqual(float, type(s), 'test_US_equity OPEN {}'.format(s))

        s = financials.getRealtime('IBM:NYQ', 'LAST_PRICE', 'FT')
        self.assertEqual(float, type(s), 'test_US_equity LAST_PRICE {}'.format(s))

        s = financials.getRealtime('IBM:NYQ', 'LOW', 'FT')
        self.assertEqual(float, type(s), 'test_US_equity LOW {}'.format(s))

        s = financials.getRealtime('IBM:NYQ', 'HIGH', 'FT')
        self.assertEqual(float, type(s), 'test_US_equity HIGH {}'.format(s))

        s = financials.getRealtime('IBM:NYQ', 'VOLUME', 'FT')
        self.assertEqual(float, type(s), 'test_US_equity VOLUME {}'.format(s))

        s = financials.getRealtime('IBM:NYQ', 'BETA', 'FT')
        self.assertTrue(testutils.is_positive_float(s), 'test_US_equity BETA {}'.format(s))

        s = financials.getRealtime('IBM:NYQ', 'EPS', 'FT')
        self.assertEqual(float, type(s), 'test_US_equity EPS {}'.format(s))

        s = financials.getRealtime('IBM:NYQ', 'SHARES_OUT', 'FT')
        self.assertEqual(float, type(s), 'test_US_equity SHARES_OUT {}'.format(s))

        s = financials.getRealtime('IBM:NYQ', 'FREE_FLOAT', 'FT')
        self.assertEqual(float, type(s), 'test_US_equity FREE_FLOAT {}'.format(s))

        s = financials.getRealtime('IBM:NYQ', 'PE_RATIO', 'FT')
        self.assertEqual(float, type(s), 'test_US_equity PE_RATIO {}'.format(s))

        s = financials.getRealtime('IBM:NYQ', 'DIV', 'FT')
        self.assertEqual(float, type(s), 'test_US_equity DIV {}'.format(s))

        s = financials.getRealtime('IBM:NYQ', 'DIV_YIELD', 'FT')
        self.assertEqual(float, type(s), 'test_US_equity DIV_YIELD {}'.format(s))

        s = financials.getRealtime('IBM:NYQ', 'EX_DIV_DATE', 'FT')
        self.assertEqual(str, type(s), 'test_US_equity EX_DIV_DATE {}'.format(s))
        self.assertTrue(testutils.is_date(s), 'test_US_equity EX_DIV_DATE {}'.format(s))

        s = financials.getRealtime('IBM:NYQ', 'PAYOUT_RATIO', 'FT')
        self.assertIsNone(s, 'test_US_equity PAYOUT_RATIO {}'.format(s))

        s = financials.getRealtime('IBM:NYQ', 'NAME', 'FT')
        self.assertEqual(str, type(s), 'test_US_equity NAME {}'.format(s))
        self.assertEqual(s, 'International Business Machines Corp', 'test_US_equity NAME {}'.format(s))

        s = financials.getRealtime('IBM:NYQ', 'SECTOR', 'FT')
        self.assertEqual(str, type(s), 'test_US_equity SECTOR {}'.format(s))
        self.assertEqual(s, 'Technology', 'test_US_equity SECTOR {}'.format(s))

        s = financials.getRealtime('IBM:NYQ', 'INDUSTRY', 'FT')
        self.assertEqual(str, type(s), 'test_US_equity INDUSTRY {}'.format(s))
        self.assertEqual(s, 'Technology', 'test_US_equity INDUSTRY {}'.format(s))

        # may fail (s is None) on weekends when date/time displayed doesn't have time component with TZ
        s = financials.getRealtime('IBM:NYQ', 'TIMEZONE', 'FT')
        self.assertEqual(str, type(s), 'test_US_equity TIMEZONE {}'.format(s))

    def test_US_mutuals(self):
        s = financials.getRealtime('VGSLX', 'LAST_PRICE', 'FT')
        self.assertEqual(float, type(s), 'test_US_mutuals LAST_PRICE {}'.format(s))

        s = financials.getRealtime('VGSLX', 'NAME', 'FT')
        self.assertEqual("Vanguard Real Estate Index Fund Admiral Shares", s, 'test_US_mutuals NAME {}'.format(s))

        s = financials.getRealtime('VGSLX', 'CURRENCY', 'FT')
        self.assertEqual('USD', s, 'test_US_mutuals CURRENCY {}'.format(s))

        s = financials.getRealtime('VGSLX', 'CHANGE', 'FT')
        self.assertEqual(float, type(s), 'test_US_mutuals CHANGE {}'.format(s))

        s = financials.getRealtime('VGSLX', 'CHANGE_IN_PERCENT', 'FT')
        self.assertEqual(float, type(s), 'test_US_mutuals CHANGE_IN_PERCENT {}'.format(s))

        s = financials.getRealtime('VFIAX', 'LAST_PRICE', 'FT')
        self.assertEqual(float, type(s), 'test_US_mutuals LAST_PRICE {}'.format(s))

        s = financials.getRealtime('VFIAX', 'LAST_PRICE_DATE', 'FT')
        self.assertEqual(str, type(s), 'test_US_mutuals LAST_PRICE_DATE {}'.format(s))
        self.assertTrue(testutils.is_date(s), 'test_US_mutuals LAST_PRICE_DATE {}'.format(s))

        s = financials.getRealtime('VFIAX', 'LAST_PRICE_TIME', 'FT')
        self.assertEqual(str, type(s), 'test_US_mutuals LAST_PRICE_TIME {}'.format(s))

    def test_US_futures(self):

        s = financials.getRealtime('ESU3:IOM', Datacode.NAME.value, 'FT')
        self.assertEqual(str, type(s), 'test_realtime_US_futures NAME {}'.format(s))
        self.assertEqual('EMINI S&P SEP3', s, 'test_US_futures NAME {}'.format(s))

        s = financials.getRealtime('ESU3:IOM', Datacode.LAST_PRICE.value, 'FT')
        self.assertEqual(float, type(s), 'test_US_futures LAST_PRICE {}'.format(s))

        # s = financials.getRealtime('ESH3:IOM', Datacode.OPEN.value, 'FT')
        # self.assertEqual(float, type(s), 'test_US_futures OPEN {}'.format(s))

        s = financials.getRealtime('ESU3:IOM', Datacode.VOLUME.value, 'FT')
        self.assertEqual(float, type(s), 'test_US_futures VOLUME {}'.format(s))

        s = financials.getRealtime('ESU3:IOM', Datacode.LOW_52_WEEK.value, 'FT')
        self.assertEqual(float, type(s), 'test_US_futures LOW_52_WEEK {}'.format(s))

        s = financials.getRealtime('ESU3:IOM', Datacode.HIGH_52_WEEK.value, 'FT')
        self.assertEqual(float, type(s), 'test_US_futures HIGH_52_WEEK {}'.format(s))

        s = financials.getRealtime('ESU3:IOM', Datacode.CHANGE.value, 'FT')
        self.assertEqual(float, type(s), 'test_US_futures CHANGE {}'.format(s))

        s = financials.getRealtime('ESU3:IOM', Datacode.CHANGE_IN_PERCENT.value, 'FT')
        self.assertEqual(float, type(s), 'test_US_futures CHANGE_IN_PERCENT {}'.format(s))

    def test_UK_ETF(self):
        s = financials.getRealtime('CSP1:LSE:GBX', 'NAME', 'FT')
        self.assertEqual(str, type(s), 'test_UK_ETF NAME {}'.format(s))
        self.assertEqual('iShares Core S&P 500 UCITS ETF USD (Acc)', s, 'test_UK_ETF NAME {}'.format(s))

        s = financials.getRealtime('VERX:LSE:GBP', 'LAST_PRICE', 'FT')
        self.assertEqual(float, type(s), 'test_UK_ETF LAST_PRICE {}'.format(s))

        s = financials.getRealtime('VERX:LSE:GBP', 'TIMEZONE', 'FT')
        self.assertEqual(str, type(s), 'test_UK_ETF TIMEZONE {}'.format(s))

    def test_UK_equity(self):
        s = financials.getRealtime('VOD:LSE', 'NAME', 'FT')
        self.assertEqual(str, type(s), 'test_UK_equity NAME {}'.format(s))
        self.assertEqual('Vodafone Group PLC', s, 'test_UK_ETF NAME {}'.format(s))

        s = financials.getRealtime('VOD:LSE', 'BID', 'FT')
        self.assertEqual(float, type(s), 'test_UK_equity BID {}'.format(s))

        s = financials.getRealtime('VOD:LSE', 'ASK', 'FT')
        self.assertEqual(float, type(s), 'test_UK_equity ASK {}'.format(s))

        s = financials.getRealtime('VOD:LSE', 'LAST_PRICE', 'FT')
        self.assertEqual(float, type(s), 'test_UK_equity LAST_PRICE {}'.format(s))

        s = financials.getRealtime('VOD:LSE', 'TIMEZONE', 'FT')
        self.assertEqual(str, type(s), 'test_UK_equity TIMEZONE {}'.format(s))

    def test_DE_equity(self):
        s = financials.getRealtime('SAPX:GER', 'NAME', 'FT')
        self.assertEqual('SAP SE', s, 'test_DE_equity NAME {}'.format(s))

        s = financials.getRealtime('SAPX:GER', 'TICKER', 'FT')
        self.assertEqual('SAPX:GER', s, 'test_DE_equity TICKER {}'.format(s))

        s = financials.getRealtime('SAPX:GER', 'CURRENCY', 'FT')
        self.assertEqual('EUR', s, 'test_DE_equity CURRENCY {}'.format(s))

        s = financials.getRealtime('SAPX:GER', 'LAST_PRICE', 'FT')
        self.assertEqual(float, type(s), 'test_DE_equity LAST_PRICE {}'.format(s))

        s = financials.getRealtime('SAPX:GER', 'CHANGE', 'FT')
        self.assertEqual(float, type(s), 'test_DE_equity CHANGE {}'.format(s))

        s = financials.getRealtime('SAPX:GER', 'CHANGE_IN_PERCENT', 'FT')
        self.assertEqual(float, type(s), 'test_DE_equity CHANGE_IN_PERCENT {}'.format(s))

        s = financials.getRealtime('SAPX:GER', 'VOLUME', 'FT')
        self.assertEqual(float, type(s), 'test_DE_equity VOLUME {}'.format(s))

        s = financials.getRealtime('SAPX:GER', 'OPEN', 'FT')
        self.assertEqual(float, type(s), 'test_DE_equity OPEN {}'.format(s))

        s = financials.getRealtime('SAPX:GER', 'HIGH', 'FT')
        self.assertEqual(float, type(s), 'test_DE_equity HIGH {}'.format(s))

        s = financials.getRealtime('SAPX:GER', 'LOW', 'FT')
        self.assertEqual(float, type(s), 'test_DE_equity LOW {}'.format(s))

        s = financials.getRealtime('SAPX:GER', 'PREV_CLOSE', 'FT')
        self.assertEqual(float, type(s), 'test_DE_equity PREV_CLOSE {}'.format(s))

        s = financials.getRealtime('SAPX:GER', 'MARKET_CAP', 'FT')
        self.assertEqual(float, type(s), 'test_DE_equity MARKET_CAP {}'.format(s))

        s = financials.getRealtime('SAPX:GER', 'SECTOR', 'FT')
        self.assertEqual(str, type(s), 'test_DE_equity SECTOR {}'.format(s))
        self.assertEqual(s, 'Technology', 'test_DE_equity SECTOR {}'.format(s))

        s = financials.getRealtime('SAPX:GER', 'INDUSTRY', 'FT')
        self.assertEqual(str, type(s), 'test_DE_equity INDUSTRY {}'.format(s))
        self.assertEqual('Technology', s, 'test_DE_equity INDUSTRY {}'.format(s))

        s = financials.getRealtime('SAPX:GER', 'LAST_PRICE_DATE', 'FT')
        self.assertEqual(str, type(s), 'test_DE_equity LAST_PRICE_DATE {}'.format(s))
        self.assertTrue(testutils.is_date(s), 'test_DE_equity LAST_PRICE_DATE {}'.format(s))

        s = financials.getRealtime('SAPX:GER', 'TIMEZONE', 'FT')
        self.assertEqual(str, type(s), 'test_DE_equity TIMEZONE {}'.format(s))

        s = financials.getRealtime('SAPX:GER', 'BETA', 'FT')
        self.assertTrue(testutils.is_positive_float(s), 'test_DE_equity BETA {}'.format(s))

        s = financials.getRealtime('SAPX:GER', 'EPS', 'FT')
        self.assertEqual(float, type(s), 'test_DE_equity EPS {}'.format(s))

        s = financials.getRealtime('SAPX:GER', 'SHARES_OUT', 'FT')
        self.assertEqual(float, type(s), 'test_DE_equity SHARES_OUT {}'.format(s))

        s = financials.getRealtime('SAPX:GER', 'FREE_FLOAT', 'FT')
        self.assertEqual(float, type(s), 'test_DE_equity FREE_FLOAT {}'.format(s))

        s = financials.getRealtime('SAPX:GER', 'PE_RATIO', 'FT')
        self.assertEqual(float, type(s), 'test_DE_equity PE_RATIO {}'.format(s))

        s = financials.getRealtime('SAPX:GER', 'DIV', 'FT')
        self.assertEqual(float, type(s), 'test_DE_equity DIV {}'.format(s))

        s = financials.getRealtime('SAPX:GER', 'DIV_YIELD', 'FT')
        self.assertEqual(float, type(s), 'test_DE_equity DIV_YIELD {}'.format(s))

        s = financials.getRealtime('SAPX:GER', 'EX_DIV_DATE', 'FT')
        self.assertEqual(str, type(s), 'test_DE_equity EX_DIV_DATE {}'.format(s))
        self.assertTrue(testutils.is_date(s), 'test_DE_equity EX_DIV_DATE {}'.format(s))

        s = financials.getRealtime('ISHAX:GER', 'NAME', 'FT')
        self.assertEqual('INTERSHOP Communications AG', s, 'test_DE_equity NAME {}'.format(s))

        s = financials.getRealtime('ISHAX:GER', 'BETA', 'FT')
        self.assertTrue(testutils.is_positive_float(s), 'test_DE_equity BETA {}'.format(s))

        s = financials.getRealtime('ISHAX:GER', 'MARKET_CAP', 'FT')
        self.assertEqual(float, type(s), 'test_DE_equity MARKET_CAP {}'.format(s))

        s = financials.getRealtime('ISHAX:GER', 'EPS', 'FT')
        self.assertEqual(float, type(s), 'test_DE_equity EPS {}'.format(s))

        s = financials.getRealtime('ISHAX:GER', 'PE_RATIO', 'FT')
        self.assertEqual(float, type(s), 'test_DE_equity PE_RATIO {}'.format(s))

        s = financials.getRealtime('ISHAX:GER', 'DIV', 'FT')
        self.assertIsNone(s, 'test_DE_equity DIV {}'.format(s))

        s = financials.getRealtime('ISHAX:GER', 'DIV_YIELD', 'FT')
        self.assertIsNone(s, 'test_DE_equity DIV_YIELD {}'.format(s))

        s = financials.getRealtime('ISHAX:GER', 'EX_DIV_DATE', 'FT')
        self.assertIsNone(s, 'test_DE_equity EX_DIV_DATE {}'.format(s))

    def test_DK_equity(self):
        s = financials.getRealtime('NOVO B:CPH', 'name', 'FT')
        self.assertEqual('Novo Nordisk A/S', s, 'test_DK_equity NAME {}'.format(s))

        s = financials.getRealtime('NOVO B:CPH', 'currency', 'FT')
        self.assertEqual('DKK', s, 'test_DK_equity CURRENCY {}'.format(s))

        s = financials.getRealtime('NOVO B:CPH', 'industry', 'FT')
        self.assertEqual(str, type(s), 'test_DK_equity INDUSTRY {}'.format(s))
        self.assertEqual('Pharmaceuticals and Biotechnology', s, 'test_DK_equity INDUSTRY {}'.format(s))

    def test_TY_equity(self):
        s = financials.getRealtime('6503:TYO', 'OPEN', 'FT')
        self.assertEqual(float, type(s), 'test_TY_equity OPEN {}'.format(s))

        s = financials.getRealtime('6503:TYO', 'LOW', 'FT')
        self.assertEqual(float, type(s), 'test_TY_equity LOW {}'.format(s))

        s = financials.getRealtime('6503:TYO', 'HIGH', 'FT')
        self.assertEqual(float, type(s), 'test_TY_equity HIGH {}'.format(s))

        s = financials.getRealtime('6503:TYO', 'LOW_52_WEEK', 'FT')
        self.assertEqual(float, type(s), 'test_TY_equity LOW_52_WEEK {}'.format(s))

        s = financials.getRealtime('6503:TYO', 'HIGH_52_WEEK', 'FT')
        self.assertEqual(float, type(s), 'test_TY_equity HIGH_52_WEEK {}'.format(s))

        s = financials.getRealtime('6503:TYO', 'MARKET_CAP', 'FT')
        self.assertEqual(float, type(s), 'test_TY_equity MARKET_CAP {}'.format(s))

        s = financials.getRealtime('6503:TYO', 'VOLUME', 'FT')
        self.assertEqual(float, type(s), 'test_TY_equity VOLUME {}'.format(s))

        s = financials.getRealtime('6503:TYO', 'CURRENCY', 'FT')
        self.assertEqual('JPY', s, 'test_TY_equity CURRENCY')

        s = financials.getRealtime('6503:TYO', 'SECTOR', 'FT')
        self.assertEqual(str, type(s), 'test_TY_equity SECTOR {}'.format(s))
        self.assertEqual('Industrials', s, 'test_TY_equity SECTOR {}'.format(s))

        s = financials.getRealtime('6503:TYO', 'INDUSTRY', 'FT')
        self.assertEqual(str, type(s), 'test_TY_equity INDUSTRY {}'.format(s))
        self.assertEqual('General Industrials', s, 'test_TY_equity INDUSTRY {}'.format(s))

    def test_TLV_equity(self):
        s = financials.getRealtime('LUMI:TLV', 'LAST_PRICE', 'FT')
        self.assertEqual(float, type(s), 'test_TLV_equity LAST_PRICE {}'.format(s))

        s = financials.getRealtime('LUMI:TLV', 'OPEN', 'FT')
        self.assertEqual(float, type(s), 'test_TLV_equity OPEN {}'.format(s))

        s = financials.getRealtime('LUMI:TLV', 'LOW', 'FT')
        self.assertEqual(float, type(s), 'test_TLV_equity LOW {}'.format(s))

        s = financials.getRealtime('LUMI:TLV', 'HIGH', 'FT')
        self.assertEqual(float, type(s), 'test_TLV_equity HIGH {}'.format(s))

        s = financials.getRealtime('LUMI:TLV', 'LOW_52_WEEK', 'FT')
        self.assertEqual(float, type(s), 'test_TLV_equity LOW_52_WEEK {}'.format(s))

        s = financials.getRealtime('LUMI:TLV', 'HIGH_52_WEEK', 'FT')
        self.assertEqual(float, type(s), 'test_TLV_equity HIGH_52_WEEK {}'.format(s))

        s = financials.getRealtime('LUMI:TLV', 'MARKET_CAP', 'FT')
        self.assertEqual(float, type(s), 'test_TLV_equity MARKET_CAP {}'.format(s))

        s = financials.getRealtime('LUMI:TLV', 'VOLUME', 'FT')
        self.assertEqual(float, type(s), 'test_TLV_equity VOLUME {}'.format(s))

        s = financials.getRealtime('LUMI:TLV', 'CURRENCY', 'FT')
        self.assertEqual('ILa', s, 'test_TLV_equity CURRENCY')

        s = financials.getRealtime('LUMI:TLV', 'SECTOR', 'FT')
        self.assertEqual(str, type(s), 'test_TLV_equity SECTOR {}'.format(s))
        self.assertEqual('Financials', s, 'test_TY_equity SECTOR {}'.format(s))

        s = financials.getRealtime('LUMI:TLV', 'INDUSTRY', 'FT')
        self.assertEqual(str, type(s), 'test_TLV_equity INDUSTRY {}'.format(s))
        self.assertEqual('Banks', s, 'test_TY_equity INDUSTRY {}'.format(s))

    def test_index(self):
        s = financials.getRealtime('INX:IOM', 'ticker', 'FT')
        self.assertEqual('INX:IOM', s, 'test_index TICKER {}'.format(s))

        s = financials.getRealtime('DAXX:GER', 'ticker', 'FT')
        self.assertEqual('DAXX:GER', s, 'test_index TICKER {}'.format(s))

        s = financials.getRealtime('DAXX:GER', 'last_price', 'FT')
        self.assertEqual(float, type(s), 'test_index LAST_PRICE {}'.format(s))

        s = financials.getRealtime('DAXX:GER', 'volume', 'FT')
        self.assertEqual(float, type(s), 'test_DE_equity VOLUME {}'.format(s))

        s = financials.getRealtime('DAXX:GER', 'low_52_week', 'FT')
        self.assertEqual(float, type(s), 'test_DE_equity LOW_52_WEEK {}'.format(s))

        s = financials.getRealtime('DAXX:GER', 'high_52_week', 'FT')
        self.assertEqual(float, type(s), 'test_DE_equity HIGH_52_WEEK {}'.format(s))

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
        self.assertEqual('Datacode is invalid', s, 'test_errors')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('unittest_args', nargs='*')
    args = parser.parse_args()
    unit_argv = [sys.argv[0]] + args.unittest_args
    unittest.main(argv=unit_argv)
