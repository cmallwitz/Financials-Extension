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
import html
import logging
import os
import pathlib
import pprint
import pytz
import re
import time
import traceback
import urllib.parse

from datacode import Datacode
from baseclient import BaseClient, HttpException
from http import cookiejar
import jsonParser


logger = logging.getLogger(__name__)
# logger.setLevel(logging.DEBUG)


def raw(m, key, default=0.0):
    try:
        return m[key]['raw']
    except:
        pass

    return default


class Yahoo(BaseClient):
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

        # use cached value for up to 5 minutes
        if ticker in self.realtime:
            tick = self.realtime[ticker]
            if time.time() - 5*60 < tick[Datacode.TIMESTAMP]:
                return self._return_value(tick, datacode)
            else:
                del self.realtime[ticker]

        url = 'https://finance.yahoo.com/quote/{}?p={}'.format(ticker, ticker)

        cookies = [cookiejar.Cookie(version=0,
                                    name="B",
                                    value="9898htldgiar5&b=3&s=gt",
                                    port=None, port_specified=None,
                                    domain=".yahoo.com", domain_specified=True, domain_initial_dot=True,
                                    path="/", path_specified=True,
                                    secure=True,
                                    expires=None,
                                    discard=False,
                                    comment=None,
                                    comment_url=None,
                                    rest=None)
                   ]

        try:
            text = self.urlopen(url, redirect=True, data=None, headers=None, cookies=cookies)
        except BaseException as e:
            logger.error(traceback.format_exc())
            return 'Yahoo.getRealtime({}, {}) - urlopen: {}'.format(ticker, datacode, e)

        try:
            text = urllib.parse.unquote(text)
            text = text.replace('\\u002F', '/')

            r = '"CrumbStore":{"crumb":"([^"]{11})"'
            pattern = re.compile(r)
            match = pattern.search(text)

            if match:
                self.crumb = match.group(1)
            else:
                with open(os.path.join(self.basedir, 'yahoo-{}.html'.format(ticker)), "w") as text_file:
                    print(text, file=text_file)

        except BaseException as e:
            logger.error(traceback.format_exc())
            return 'Yahoo.getRealtime({}, {}) - crumb: {}'.format(ticker, datacode, e)

        try:
            start = text.find('"QuoteSummaryStore":{')

            if start < 0:
                with open(os.path.join(self.basedir, 'yahoo-{}.html'.format(ticker)), "w") as text_file:
                    print(text, file=text_file)
                return None

            start = start + len('"QuoteSummaryStore":')
            results = self.js.parseString(text[start:])

            if not results:
                with open(os.path.join(self.basedir, 'yahoo-{}.html'.format(ticker)), "w") as text_file:
                    print(text, file=text_file)
                return None

        except BaseException as e:
            logger.error(traceback.format_exc())
            return 'Yahoo.getRealtime({}, {}) - parsing: {}'.format(ticker, datacode, e)

        try:
            price = results['price']
            quoteType = results['quoteType']
            summaryDetail = results['summaryDetail']

            if not price:
                return 'Could not find price for \'{}\''.format(ticker)

            if ticker not in self.realtime:
                self.realtime[ticker] = {}

            tick = self.realtime[ticker]

            tick[Datacode.PREV_CLOSE] = float(raw(price, 'regularMarketPreviousClose'))
            tick[Datacode.OPEN] = float(raw(price, 'regularMarketOpen'))
            tick[Datacode.CHANGE] = float(raw(price, 'regularMarketChange'))
            tick[Datacode.CHANGE_IN_PERCENT] = 100 * float(raw(price, 'regularMarketChangePercent'))
            tick[Datacode.LOW] = float(raw(price, 'regularMarketDayLow'))
            tick[Datacode.HIGH] = float(raw(price, 'regularMarketDayHigh'))
            tick[Datacode.LAST_PRICE] = float(raw(price, 'regularMarketPrice'))
            tick[Datacode.VOLUME] = float(raw(price, 'regularMarketVolume'))
            tick[Datacode.AVG_DAILY_VOL_3MOMTH] = float(raw(price, 'averageDailyVolume3Month'))

            tick[Datacode.LOW_52_WEEK] = float(raw(summaryDetail, 'fiftyTwoWeekLow'))
            tick[Datacode.HIGH_52_WEEK] = float(raw(summaryDetail, 'fiftyTwoWeekHigh'))
            tick[Datacode.MARKET_CAP] = float(raw(summaryDetail, 'marketCap'))

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

            name = price['longName'] or price['shortName']
            if name:
                tick[Datacode.NAME] = html.unescape(str(name))
            else:
                tick[Datacode.NAME] = ''

            tick[Datacode.TIMESTAMP] = time.time()

        except BaseException as e:
            with open(os.path.join(self.basedir, 'yahoo-{}.js'.format(ticker)), "w") as text_file:
                pprint.pprint(results.asList(), stream=text_file)

            logger.error(traceback.format_exc())
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
        min_tick_date = None

        # dividend and splits will change past adjusted prices
        # the moment we are asked for ADJ_CLOSE we ignore the ticker cache to refresh

        if Datacode.ADJ_CLOSE != datacode and ticker not in self.historicdata:
            self._read_ticker_csv_file(ticker)

        if ticker in self.historicdata:
            ticks = self.historicdata[ticker]

            if date in ticks:
                return self._return_value(ticks[date], datacode)

            # weekend, trading holiday or as yet un-fetched
            if min(ticks) <= date <= max(ticks):
                return 'Not a trading day \'{}\''.format(date)

            # (potentially) future date
            if date > max(ticks):
                t1 = int(dateutil.parser.parse(date).strftime('%s'))
                t2 = int(time.time())
                if t1 > t2:
                    return 'Future date \'{}\''.format(date)

                min_tick_date = int(dateutil.parser.parse(min(ticks)).strftime('%s'))  # remember current earliest date

        if not self.crumb:
            self.getRealtime(ticker, datacode)

        if not self.crumb:
            return 'Yahoo.getHistoric({}, {}, {}) - crumb'.format(ticker, datacode, date)

        try:
            t1 = int(dateutil.parser.parse(date).strftime('%s'))
            t2 = int(time.time())

            if min_tick_date:
                t1 = min_tick_date

            if t1 >= t2:
                return 'Future date \'{}\''.format(date)

            if t1 < int(dateutil.parser.parse('2000-01-01').strftime('%s')):
                return 'Date before 2000 \'{}\''.format(date)

            t1 = t1 - 2682000  # pad with extra month

        except BaseException as e:
            logger.error(traceback.format_exc())
            return 'Yahoo.getHistoric({}, {}, {}) - date: {}'.format(ticker, datacode, date, e)

        try:

            url = 'https://query1.finance.yahoo.com/v7/finance/download/{}' \
                  '?period1={}&period2={}&interval=1d&events=history&crumb={}' \
                .format(ticker, t1, t2, urllib.parse.quote_plus(self.crumb))

            text = self.urlopen(url)

            with open(os.path.join(self.basedir, 'yahoo-{}.csv'.format(ticker)), "w") as csv_file:
                print(text, file=csv_file)

            self._read_ticker_csv_file(ticker)

        except HttpException:
            logger.error(traceback.format_exc())
            return None

        except BaseException as e:
            logger.error(traceback.format_exc())
            return 'Yahoo.getHistoric({}, {}, {}) - read: {}'.format(ticker, datacode, date, e)

        try:
            if ticker in self.historicdata:
                ticks = self.historicdata[ticker]

                if date in ticks:
                    return self._return_value(ticks[date], datacode)

                # future date
                if date > max(ticks):
                    return 'Future date \'{}\''.format(date)

                # weekend or trading holiday
                return 'Not a trading day \'{}\''.format(date)

        except BaseException as e:
            logger.error(traceback.format_exc())
            return 'Yahoo.getHistoric({}, {}, {}) - process: {}'.format(ticker, datacode, date, e)

        return None


def createInstance(ctx):
    return Yahoo(ctx)
