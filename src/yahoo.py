#  yahoo.py
#
#  license: GNU LGPL
#
#  This library is free software; you can redistribute it and/or
#  modify it under the terms of the GNU Lesser General Public
#  License as published by the Free Software Foundation; either
#  version 3 of the License, or (at your option) any later version.


import csv
import datetime
import dateutil.parser
import os
import pathlib
import pprint
import pytz
import re
import sys
import time
import traceback
import urllib.parse

from datacode import Datacode
import baseclient
import jsonParser


def log(str):
    print(str, file=sys.stderr)
    # pass


class Yahoo(baseclient.BaseClient):
    def __init__(self, ctx):
        super().__init__()

        self.crumb = None
        self.realtime = {}
        self.historicdata = {}
        self.js = jsonParser.jsonObject

        self.basedir = os.path.join(str(pathlib.Path.home()), '.financials-extension')
        os.makedirs(self.basedir, exist_ok=True)

    def _read_ticker_csv_file(self, ticker):

        fn = os.path.join(self.basedir, 'yahoo-{}.csv'.format(ticker))

        if not os.path.isfile(fn):
            return

        with open(fn, newline='') as csvfile:
            reader = csv.DictReader(csvfile)

            ticks = {}

            for row in reader:
                tick = {}
                try:
                    tick[Datacode.OPEN] = float(row['Open'])
                    tick[Datacode.LOW] = float(row['Low'])
                    tick[Datacode.HIGH] = float(row['High'])
                    tick[Datacode.VOLUME] = float(row['Volume'])
                    tick[Datacode.CLOSE] = float(row['Close'])
                    tick[Datacode.ADJ_CLOSE] = float(row['Adj Close'])
                except:
                    pass

                if len(tick) > 0:
                    ticks[row['Date']] = tick

            self.historicdata[ticker] = ticks

    def getRealtime(self, ticker, datacode):

        """
        Retrieve realtime data for ticker from Yahoo Finance and cache it for further lookups

        :param ticker: the ticker symbol e.g. VOD.L or LON:VOD
        :param datacode: the requested datacode
        :return:
        """

        # remove white space
        ticker = "".join(ticker.split())

        # use cached value for up to 60 seconds
        if ticker in self.realtime:
            tick = self.realtime[ticker]
            if time.time() - 60 < tick[Datacode.TIMESTAMP]:
                return self._return_value(tick, datacode)
            else:
                del self.realtime[ticker]

        url = 'https://finance.yahoo.com/quote/{}?p={}'.format(ticker, ticker)

        try:
            text = self.urlopen(url)
        except BaseException as e:
            log(traceback.format_exc())
            return 'Yahoo.getRealtime({}, {}) - urlopen: {}'.format(ticker, datacode, e)

        try:
            text = urllib.parse.unquote(text)
            text = text.replace('\\u002F', '/')

            r = '"CrumbStore":{"crumb":"([^"]{11})"'
            pattern = re.compile(r)
            match = re.search(pattern, text)

            if match:
                self.crumb = match.group(1)
            else:
                with open(os.path.join(self.basedir, 'yahoo-{}.html'.format(ticker)), "w") as text_file:
                    print(text, file=text_file)

        except BaseException as e:
            log(traceback.format_exc())
            return 'Yahoo.getRealtime({}, {}) - crumb: {}'.format(ticker, datacode, e)

        try:
            start = text.find('"QuoteSummaryStore":{')

            if start < 0:
                with open(os.path.join(self.basedir, 'yahoo-{}.html'.format(ticker)), "w") as text_file:
                    print(text, file=text_file)

                return 'Could not find QuoteSummaryStore for \'{}\''.format(ticker)

            start = start + len('"QuoteSummaryStore":')
            results = self.js.parseString(text[start:])

            if not results:
                with open(os.path.join(self.basedir, 'yahoo-{}.html'.format(ticker)), "w") as text_file:
                    print(text, file=text_file)
                return None

            price = results['price']
            quoteType = results['quoteType']

            if not price:
                return 'Could not find price for \'{}\''.format(ticker)

            if ticker not in self.realtime:
                self.realtime[ticker] = {}

            tick = self.realtime[ticker]

            tick[Datacode.PREV_CLOSE] = float(price['regularMarketPreviousClose']['raw'])
            tick[Datacode.OPEN] = float(price['regularMarketOpen']['raw'])
            tick[Datacode.CHANGE] = float(price['regularMarketChange']['raw'])
            tick[Datacode.CHANGE_IN_PERCENT] = float(price['regularMarketChangePercent']['raw'])
            tick[Datacode.LOW] = float(price['regularMarketDayLow']['raw'])
            tick[Datacode.HIGH] = float(price['regularMarketDayHigh']['raw'])
            tick[Datacode.LAST_PRICE] = float(price['regularMarketPrice']['raw'])
            tick[Datacode.VOLUME] = float(price['regularMarketVolume']['raw'])
            tick[Datacode.AVG_DAILY_VOL_3MOMTH] = float(price['averageDailyVolume3Month']['raw'])

            if quoteType:
                t = int(price['regularMarketTime'])
                tz = pytz.timezone(quoteType['exchangeTimezoneName'])

                tick[Datacode.TIMEZONE] = tz
                dt = datetime.datetime.fromtimestamp(t, tz)

                tick[Datacode.LAST_PRICE_DATE] = dt.date()
                tick[Datacode.LAST_PRICE_TIME] = dt.time()

            tick[Datacode.TICKER] = str(price['symbol'])
            tick[Datacode.EXCHANGE] = str(price['exchange'])
            tick[Datacode.CURRENCY] = str(price['currency'])
            tick[Datacode.NAME] = str(price['longName'])

            tick[Datacode.TIMESTAMP] = time.time()

        except BaseException as e:
            with open(os.path.join(self.basedir, 'yahoo-{}.js'.format(ticker)), "w") as text_file:
                pprint.pprint(results.asList(), stream=text_file)

            log(traceback.format_exc())
            return 'Yahoo.getRealtime({}, {}) - process: {}'.format(ticker, datacode, e)

        return self._return_value(self.realtime[ticker], datacode)

    def getHistoric(self, ticker: str, datacode: int, date):

        """
        Retrieve historic data for ticker from Yahoo Finance and cache it for further lookups

        :param ticker: the ticker symbol e.g. VOD.L or LON:VOD
        :param datacode: the requested datacode
        :param date: the requested date
        :return:
        """

        # remove white space
        ticker = "".join(ticker.split())

        if ticker not in self.historicdata:
            self._read_ticker_csv_file(ticker)

        if ticker in self.historicdata:
            ticks = self.historicdata[ticker]

            if date in ticks:
                return self._return_value(ticks[date], datacode)

            if date > max(ticks):
                return 'Future date \'{}\''.format(date)

            # weekend or trading holiday
            if date >= min(ticks):  # or date <= max(ticks):
                return 'Not a trading day \'{}\''.format(date)

        if not self.crumb:
            self.getRealtime(ticker, datacode)

        if not self.crumb:
            return 'Yahoo.getHistoric({}, {}, {}) - crumb'.format(ticker, datacode, date)

        try:
            t1 = int(dateutil.parser.parse(date).strftime('%s'))
            t2 = int(time.time())

            if t1 >= t2:
                return 'Future date \'{}\''.format(date)

            if t1 < int(dateutil.parser.parse('2000-01-01').strftime('%s')):
                return 'Date before 2000 \'{}\''.format(date)

            t1 = t1 - 2682000  # pad with extra month

        except BaseException as e:
            log(traceback.format_exc())
            return 'Yahoo.getHistoric({}, {}, {}) - date: {}'.format(ticker, datacode, date, e)

        try:

            url = 'https://query1.finance.yahoo.com/v7/finance/download/{}' \
                  '?period1={}&period2={}&interval=1d&events=history&crumb={}'.format(
                ticker, t1, t2, urllib.parse.quote_plus(self.crumb))

            text = self.urlopen(url)

            with open(os.path.join(self.basedir, 'yahoo-{}.csv'.format(ticker)), "w") as csv_file:
                print(text, file=csv_file)

            self._read_ticker_csv_file(ticker)

        except BaseException as e:
            log(traceback.format_exc())
            return 'Yahoo.getHistoric({}, {}, {}) - read: {}'.format(ticker, datacode, date, e)

        try:
            if ticker in self.historicdata:
                ticks = self.historicdata[ticker]

                if date in ticks:
                    return self._return_value(ticks[date], datacode)

                # weekend or trading holiday
                if date >= min(ticks) or date <= max(ticks):
                    return 'Not a trading day \'{}\''.format(date)

        except BaseException as e:
            log(traceback.format_exc())
            return 'Yahoo.getHistoric({}, {}, {}) - process: {}'.format(ticker, datacode, date, e)

        return None


def createInstance(ctx):
    return Yahoo(ctx)
