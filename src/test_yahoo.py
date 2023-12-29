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

import baseclient
import financials
from datacode import Datacode
import testutils

financials = financials.createInstance(None)


def urlopen_fail(self, url, redirect=True, data=None, headers={}, cookies=[], **kwargs):
    raise baseclient.HttpException(url, 'ERROR: simulated urlopen() failed')


class Test(unittest.TestCase):

    @classmethod
    def tearDownClass(cls):
        # this avoids "ResourceWarning: unclosed..." on cached socket connections
        financials.close()

    def test_recovery_from_urlopen_error_issue(self):

        financials.yahoo.last_url = 'blank'

        urlopen_saved = baseclient.BaseClient.urlopen
        baseclient.BaseClient.urlopen = urlopen_fail

        s = financials.getRealtime('U1IH.F', Datacode.LAST_PRICE.value, 'YAHOO')

        baseclient.BaseClient.urlopen = urlopen_saved

        s = financials.getRealtime('U1IH.F', Datacode.PREV_CLOSE.value, 'YAHOO')
        self.assertEqual(float, type(s), 'test_recovery_from_urlopen_error_issue PREV_CLOSE {}'.format(s))

    def test_currency(self):
        s = financials.getRealtime('EURGBP=X', Datacode.CURRENCY.value, 'YAHOO')
        self.assertEqual(str, type(s), 'test_currency CURRENCY')

        s = financials.getRealtime('EURGBP=X', Datacode.LAST_PRICE.value, 'YAHOO')
        self.assertEqual(float, type(s), 'test_currency LAST_PRICE')

    def test_realtime_US_ZVZZT(self):

        s = financials.getRealtime('ZVZZT', Datacode.PAYOUT_RATIO.value, 'YAHOO')
        self.assertIsNone(s, 'test_realtime_US_ZVZZT PAYOUT_RATIO {}'.format(s))

        s = financials.getRealtime('ZVZZT', Datacode.SECTOR.value, 'YAHOO')
        self.assertIsNone(s, 'test_realtime_US_ZVZZT SECTOR {}'.format(s))

        s = financials.getRealtime('ZVZZT', Datacode.LAST_PRICE.value, 'YAHOO')
        self.assertEqual(float, type(s), 'test_realtime_US_ZVZZT LAST_PRICE {}'.format(s))

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
        self.assertEqual(s, 'International Business Machines Corporation (IBM)',
                         'test_realtime_US_equity NAME {}'.format(s))

        s = financials.getRealtime('IBM', 'SECTOR', 'YAHOO')
        self.assertEqual(str, type(s), 'test_realtime_US_equity SECTOR {}'.format(s))
        self.assertEqual(s, 'Technology', 'test_realtime_US_equity SECTOR {}'.format(s))

        s = financials.getRealtime('IBM', 'INDUSTRY', 'YAHOO')
        self.assertEqual(str, type(s), 'test_realtime_US_equity INDUSTRY {}'.format(s))
        self.assertEqual(s, 'Information Technology Services', 'test_realtime_US_equity INDUSTRY {}'.format(s))

        s = financials.getRealtime('IBM', Datacode.TIMEZONE.value, 'YAHOO')
        self.assertTrue(s == 'EST' or s == 'EDT', 'test_realtime_US_equity TIMEZONE: {}'.format(s))

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

        s = financials.getRealtime('IBM', 'PAYOUT_RATIO', 'YAHOO')
        self.assertTrue(testutils.is_positive_float(s), 'test_realtime_US_equity PAYOUT_RATIO {}'.format(s))

        s = financials.getRealtime('IBM', 'SHARES_OUT', 'YAHOO')
        self.assertTrue(testutils.is_positive_float(s), 'test_realtime_US_equity SHARES_OUT {}'.format(s))

        s = financials.getRealtime('IBM', 'FREE_FLOAT', 'YAHOO')
        self.assertTrue(testutils.is_positive_float(s), 'test_realtime_US_equity FREE_FLOAT {}'.format(s))

        s = financials.getRealtime('IBM', Datacode.EXCHANGE.value, 'YAHOO')
        self.assertEqual(s, 'NYSE', 'test_realtime_US_equity EXCHANGE')

    def test_realtime_US_mutuals(self):

        s = financials.getRealtime('VGSLX', Datacode.LAST_PRICE.value, 'YAHOO')
        self.assertEqual(float, type(s), 'test_realtime_US_mutuals LAST_PRICE {}'.format(s))

        s = financials.getRealtime('VFIAX', Datacode.LAST_PRICE.value, 'YAHOO')
        self.assertEqual(float, type(s), 'test_realtime_US_mutuals LAST_PRICE {}'.format(s))

        s = financials.getRealtime('VFIAX', Datacode.DIV.value, 'YAHOO')
        self.assertEqual(float, type(s), 'test_realtime_US_mutuals DIV {}'.format(s))

        s = financials.getRealtime('VFIAX', Datacode.DIV_YIELD.value, 'YAHOO')
        # self.assertIsNone(s, 'test_realtime_US_mutuals DIV_YIELD {}'.format(s)) # no yield
        self.assertTrue(testutils.is_positive_float(s), 'test_realtime_US_mutuals DIV_YIELD {}'.format(s))

        s = financials.getRealtime('SHRAX', Datacode.DIV.value, 'YAHOO')
        self.assertEqual(float, type(s), 'test_realtime_US_mutuals DIV {}'.format(s))

        s = financials.getRealtime('SHRAX', Datacode.DIV_YIELD.value, 'YAHOO')
        # self.assertIsNone(s, 'test_realtime_US_mutuals DIV_YIELD {}'.format(s)) # no yield
        self.assertEqual(float, type(s), 'test_realtime_US_mutuals DIV_YIELD {}'.format(s))

        # s = financials.getRealtime('VERX.L', Datacode.DIV.value, 'YAHOO')
        # self.assertIsNone(s, 'test_realtime_US_mutuals DIV {}'.format(s)) # no dividend

        s = financials.getRealtime('VERX.L', Datacode.DIV_YIELD.value, 'YAHOO')
        self.assertIsNone(s, 'test_realtime_US_mutuals DIV_YIELD {}'.format(s)) # no yield
        # self.assertEqual(float, type(s), 'test_realtime_US_mutuals DIV_YIELD {}'.format(s))

    def test_realtime_US_options(self):

        # symbol from https://finance.yahoo.com/quote/IBM/options?p=IBM
        
        s = financials.getRealtime('IBM250117C00165000', Datacode.PREV_CLOSE.value, 'YAHOO')
        self.assertEqual(float, type(s), 'test_realtime_US_options PREV_CLOSE {}'.format(s))

        s = financials.getRealtime('IBM250117C00165000', Datacode.NAME.value, 'YAHOO')
        self.assertEqual(str, type(s), 'test_realtime_US_options NAME {}'.format(s))
        self.assertEqual('IBM Jan 2025 165.000 call', s, 'test_realtime_US_options NAME {}'.format(s))

        s = financials.getRealtime('IBM250117C00165000', Datacode.EXPIRY_DATE.value, 'YAHOO')
        self.assertEqual(str, type(s), 'test_realtime_US_options EXPIRY_DATE {}'.format(s))
        self.assertTrue(testutils.is_date(s), 'test_realtime_US_options EXPIRY_DATE {}'.format(s))
        self.assertEqual("2025-01-17", s, 'test_realtime_US_options EXPIRY_DATE {}'.format(s))

        s = financials.getRealtime('IBM250117C00165000', Datacode.LAST_PRICE.value, 'YAHOO')
        self.assertEqual(float, type(s), 'test_realtime_US_options LAST_PRICE {}'.format(s))

        s = financials.getRealtime('IBM250117C00165000', Datacode.OPEN.value, 'YAHOO')
        self.assertEqual(float, type(s), 'test_realtime_US_options OPEN {}'.format(s))

        s = financials.getRealtime('IBM250117C00165000', Datacode.VOLUME.value, 'YAHOO')
        self.assertEqual(float, type(s), 'test_realtime_US_options VOLUME {}'.format(s))

        s = financials.getRealtime('IBM250117C00165000', Datacode.BID.value, 'YAHOO')
        self.assertEqual(float, type(s), 'test_realtime_US_options BID {}'.format(s))

        s = financials.getRealtime('IBM250117C00165000', Datacode.ASK.value, 'YAHOO')
        self.assertEqual(float, type(s), 'test_realtime_US_options ASK {}'.format(s))

        s = financials.getRealtime('IBM250117C00165000', Datacode.PAYOUT_RATIO.value, 'YAHOO')
        self.assertIsNone(s, 'test_realtime_US_options PAYOUT_RATIO {}'.format(s))

        s = financials.getRealtime('IBM250117C00165000', Datacode.SECTOR.value, 'YAHOO')
        self.assertIsNone(s, 'test_realtime_US_options SECTOR {}'.format(s))

    def test_realtime_US_futures(self):

        s = financials.getRealtime('ES=F', Datacode.NAME.value, 'YAHOO')
        self.assertEqual(str, type(s), 'test_realtime_US_futures NAME {}'.format(s))
        self.assertEqual('E-Mini S&P 500 Mar 24 (ES=F)', s, 'test_realtime_US_futures NAME {}'.format(s))

        s = financials.getRealtime('ES=F', Datacode.TICKER.value, 'YAHOO')
        self.assertEqual(str, type(s), 'test_realtime_US_futures TICKER {}'.format(s))
        self.assertEqual('ESH24.CME', s, 'test_realtime_US_futures TICKER {}'.format(s))

        s = financials.getRealtime('ES=F', Datacode.SETTLEMENT_DATE.value, 'YAHOO')
        self.assertEqual(str, type(s), 'test_realtime_US_futures SETTLEMENT_DATE {}'.format(s))
        self.assertTrue(testutils.is_date(s), 'test_realtime_US_futures SETTLEMENT_DATE {}'.format(s))
        self.assertEqual("2024-03-15", s, 'test_realtime_US_futures SETTLEMENT_DATE {}'.format(s))

        s = financials.getRealtime('ES=F', Datacode.LAST_PRICE.value, 'YAHOO')
        self.assertEqual(float, type(s), 'test_realtime_US_futures LAST_PRICE {}'.format(s))

        s = financials.getRealtime('ES=F', Datacode.OPEN.value, 'YAHOO')
        self.assertEqual(float, type(s), 'test_realtime_US_futures OPEN {}'.format(s))

        s = financials.getRealtime('ES=F', Datacode.VOLUME.value, 'YAHOO')
        self.assertEqual(float, type(s), 'test_realtime_US_futures VOLUME {}'.format(s))

        s = financials.getRealtime('ES=F', Datacode.BID.value, 'YAHOO')
        self.assertEqual(float, type(s), 'test_realtime_US_futures BID {}'.format(s))

        s = financials.getRealtime('ES=F', Datacode.ASK.value, 'YAHOO')
        self.assertEqual(float, type(s), 'test_realtime_US_futures ASK {}'.format(s))

        s = financials.getRealtime('ES=F', Datacode.CHANGE.value, 'YAHOO')
        self.assertEqual(float, type(s), 'test_realtime_US_futures CHANGE {}'.format(s))

        s = financials.getRealtime('ES=F', Datacode.CHANGE_IN_PERCENT.value, 'YAHOO')
        self.assertEqual(float, type(s), 'test_realtime_US_futures CHANGE_IN_PERCENT {}'.format(s))

        s = financials.getRealtime('ES=F', Datacode.LOW.value, 'YAHOO')
        self.assertEqual(float, type(s), 'test_realtime_US_futures LOW {}'.format(s))

        s = financials.getRealtime('ES=F', Datacode.HIGH.value, 'YAHOO')
        self.assertEqual(float, type(s), 'test_realtime_US_futures HIGH {}'.format(s))

    def test_realtime_UK_ETF(self):

        s = financials.getRealtime('VERX.L', Datacode.LAST_PRICE.value, 'YAHOO')
        self.assertEqual(float, type(s), 'test_realtime_UK_ETF LAST_PRICE {}'.format(s))

        s = financials.getRealtime('VERX.L', Datacode.TIMEZONE.value, 'YAHOO')
        self.assertTrue(s == 'GMT' or s == 'BST', 'test_realtime_UK_ETF TIMEZONE: {}'.format(s))

        s = financials.getRealtime('CSP1.L', Datacode.NAME.value, 'YAHOO')
        self.assertEqual(str, type(s), 'test_realtime_UK_ETF NAME {}'.format(s))
        self.assertEqual('iShares VII PLC - iShares Core S&P 500 UCITS ETF (CSP1.L)', s, 'test_realtime_UK_ETF NAME {}'.format(s))

        s = financials.getRealtime('VERX.L', 'SECTOR', 'YAHOO')
        self.assertIsNone(s, 'test_realtime_UK_ETF SECTOR {}'.format(s))

        s = financials.getRealtime('VERX.L', 'INDUSTRY', 'YAHOO')
        self.assertIsNone(s, 'test_realtime_UK_ETF INDUSTRY {}'.format(s))

        s = financials.getRealtime('VERX.L', 'PAYOUT_RATIO', 'YAHOO')
        self.assertIsNone(s, 'test_realtime_UK_ETF PAYOUT_RATIO {}'.format(s))

        s = financials.getRealtime('VERX.L', 'SHARES_OUT', 'YAHOO')
        self.assertIsNone(s, 'test_realtime_UK_ETF SHARES_OUT {}'.format(s))

    def test_realtime_DE_equity(self):

        s = financials.getRealtime('SAP.DE', Datacode.LAST_PRICE.value, 'YAHOO')
        self.assertEqual(float, type(s), 'test_realtime_DE_equity LAST_PRICE {}'.format(s))

        s = financials.getRealtime('SAP.DE', Datacode.TIMEZONE.value, 'YAHOO')
        self.assertTrue(s == 'CET' or s == 'CEST', 'test_realtime_DE_equity TIMEZONE: {}'.format(s))

        s = financials.getRealtime('SAP.DE', Datacode.SECTOR.value, 'YAHOO')
        self.assertEqual(str, type(s), 'test_realtime_DE_equity SECTOR {}'.format(s))
        self.assertEqual('Technology', s, 'test_realtime_DE_equity SECTOR {}'.format(s))

        s = financials.getRealtime('SAP.DE', Datacode.INDUSTRY.value, 'YAHOO')
        self.assertEqual(str, type(s), 'test_realtime_DE_equity INDUSTRY {}'.format(s))
        self.assertEqual(s, 'Software - Application', 'test_realtime_DE_equity INDUSTRY {}'.format(s))

        s = financials.getRealtime('LYY8.DE', Datacode.NAME.value, 'YAHOO')
        self.assertEqual(str, type(s), 'test_realtime_DE_equity NAME {}'.format(s))

        s = financials.getRealtime('LYY8.DE', Datacode.EXCHANGE.value, 'YAHOO')
        self.assertEqual(s, 'XETRA', 'test_realtime_DE_equity EXCHANGE')

    def test_TA_equity(self):

        s = financials.getRealtime('LUMI.TA', 'LAST_PRICE', 'YAHOO')
        self.assertEqual(float, type(s), 'test_TA_equity LAST_PRICE {}'.format(s))

        s = financials.getRealtime('LUMI.TA', 'OPEN', 'YAHOO')
        self.assertEqual(float, type(s), 'test_TA_equity OPEN {}'.format(s))

        s = financials.getRealtime('LUMI.TA', 'LOW', 'YAHOO')
        self.assertEqual(float, type(s), 'test_TA_equity LOW {}'.format(s))

        s = financials.getRealtime('LUMI.TA', 'HIGH', 'YAHOO')
        self.assertEqual(float, type(s), 'test_TA_equity HIGH {}'.format(s))

        s = financials.getRealtime('LUMI.TA', 'LOW_52_WEEK', 'YAHOO')
        self.assertEqual(float, type(s), 'test_TA_equity LOW_52_WEEK {}'.format(s))

        s = financials.getRealtime('LUMI.TA', 'HIGH_52_WEEK', 'YAHOO')
        self.assertEqual(float, type(s), 'test_TA_equity HIGH_52_WEEK {}'.format(s))

        s = financials.getRealtime('LUMI.TA', 'MARKET_CAP', 'YAHOO')
        self.assertEqual(float, type(s), 'test_TA_equity MARKET_CAP {}'.format(s))

        s = financials.getRealtime('LUMI.TA', 'VOLUME', 'YAHOO')
        self.assertEqual(float, type(s), 'test_TA_equity VOLUME {}'.format(s))

        s = financials.getRealtime('LUMI.TA', 'CURRENCY', 'YAHOO')
        self.assertEqual('ILA', s, 'test_TA_equity CURRENCY')

        s = financials.getRealtime('LUMI.TA', 'SECTOR', 'YAHOO')
        self.assertEqual(str, type(s), 'test_TLV_equity SECTOR {}'.format(s))
        self.assertEqual('Financial Services', s, 'test_TA_equity SECTOR {}'.format(s))

        s = financials.getRealtime('LUMI.TA', 'INDUSTRY', 'YAHOO')
        self.assertEqual(str, type(s), 'test_TLV_equity INDUSTRY {}'.format(s))
        self.assertEqual('Banks - Regional', s, 'test_TA_equity INDUSTRY {}'.format(s))

    def test_DK_equity(self):
        s = financials.getRealtime('NOVO-B.CO', 'last_price', 'YAHOO')
        self.assertEqual(float, type(s), 'test_DK_equity LAST_PRICE {}'.format(s))

        s = financials.getRealtime('NOVO-B.CO', 'name', 'YAHOO')
        self.assertEqual('Novo Nordisk A/S (NOVO-B.CO)', s, 'test_DK_equity NAME {}'.format(s))

        s = financials.getRealtime('NOVO-B.CO', 'currency', 'YAHOO')
        self.assertEqual('DKK', s, 'test_DK_equity CURRENCY {}'.format(s))

        s = financials.getRealtime('NOVO-B.CO', 'industry', 'YAHOO')
        self.assertEqual(str, type(s), 'test_DK_equity INDUSTRY {}'.format(s))
        self.assertEqual('Biotechnology', s, 'test_DK_equity INDUSTRY {}'.format(s))

        s = financials.getRealtime('MAERSK-B.CO', 'currency', 'YAHOO')
        self.assertEqual('DKK', s, 'test_DK_equity CURRENCY {}'.format(s))

    def test_realtime_TY_equity(self):
        s = financials.getRealtime('6503.T', Datacode.SECTOR.value, 'YAHOO')
        self.assertEqual(str, type(s), 'test_TY_equity SECTOR {}'.format(s))
        self.assertEqual(s, 'Industrials', 'test_TY_equity SECTOR {}'.format(s))

        s = financials.getRealtime('6503.T', Datacode.INDUSTRY.value, 'YAHOO')
        self.assertEqual(str, type(s), 'test_TY_equity INDUSTRY {}'.format(s))
        self.assertEqual(s, 'Electrical Equipment & Parts', 'test_TY_equity INDUSTRY {}'.format(s))

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

        s = financials.getRealtime('6503.T', Datacode.TIMEZONE.value, 'YAHOO')
        self.assertEqual(s, 'JST', 'test_TY_equity TIMEZONE')

    def test_historic_US_equity(self):

        s = financials.getHistoric('IBM', Datacode.LAST_PRICE.value, '2017-01-01', 'YAHOO')
        self.assertEqual('Not a trading day \'2017-01-01\'', s, 'test_historic_US_equity LAST_PRICE {}'.format(s))

        s = financials.getHistoric('IBM', Datacode.CLOSE.value, '2017-01-01', 'YAHOO')
        self.assertEqual('Not a trading day \'2017-01-01\'', s, 'test_historic_US_equity CLOSE {}'.format(s))

        s = financials.getHistoric('IBM', Datacode.LAST_PRICE.value, '2017-01-03', 'YAHOO')
        self.assertIsNone(s, 'test_historic_US_equity LAST_PRICE {}'.format(s))

        s = financials.getHistoric('IBM', Datacode.CLOSE.value, '2017-01-03', 'YAHOO')
        self.assertEqual(159.837479, s, 'test_historic_US_equity CLOSE {}'.format(s))

        financials.yahoo.historicdata = {}

        s = financials.getHistoric('IBM', Datacode.CLOSE.value, '2017-01-03', 'YAHOO')
        self.assertEqual(159.837479, s, 'test_historic_US_equity CLOSE {}'.format(s))

        directory = os.path.join(str(pathlib.Path.home()), '.financials-extension')
        ibm = os.path.join(directory, 'yahoo-IBM.csv')
        try:
            os.unlink(ibm)
        except:
            pass  # ignore if file doesn't exists

        financials.yahoo.historicdata = {}

        s = financials.getHistoric('IBM', Datacode.CLOSE.value, '2017-01-03', 'YAHOO')
        self.assertEqual(159.837479, s, 'test_historic_US_equity CLOSE {}'.format(s))

        s = financials.getHistoric('IBM', Datacode.ADJ_CLOSE.value, '2017-01-03', 'YAHOO')
        self.assertEqual(float, type(s), 'test_historic_US_equity ADJ_CLOSE {}'.format(s))

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

        s = financials.getHistoric('LYY8.DE', Datacode.CLOSE.value, '2017-01-03', 'YAHOO')
        self.assertEqual(s, 96.010002, 'test_historic_DE_equity CLOSE {}'.format(s))

    def test_realtime_errors(self):

        s = financials.getRealtime('NO_NAME', Datacode.LAST_PRICE.value, 'YAHOO')
        self.assertIsNone(s, 'test_realtime_errors LAST_PRICE {}'.format(s))

        s = financials.getRealtime('NO_NAME', Datacode.PAYOUT_RATIO.value, 'YAHOO')
        self.assertIsNone(s, 'test_realtime_errors PAYOUT_RATIO {}'.format(s))

        s = financials.getRealtime('NO_NAME', Datacode.SECTOR.value, 'YAHOO')
        self.assertIsNone(s, 'test_realtime_errors SECTOR {}'.format(s))

        s = financials.getRealtime('LYY8.DE', -1, 'YAHOO')
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
