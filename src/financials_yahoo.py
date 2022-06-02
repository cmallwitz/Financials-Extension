#  financials_yahoo.py
#
#  license: GNU LGPL
#
#  This library is free software; you can redistribute it and/or
#  modify it under the terms of the GNU Lesser General Public
#  License as published by the Free Software Foundation; either
#  version 3 of the License, or (at your option) any later version.


import csv
import datetime
import html
import logging
import os
import pprint
import re
import time
import urllib.parse
from http import cookiejar

import dateutil.parser
import pytz

import jsonParser
from baseclient import BaseClient, HttpException
from datacode import Datacode

logger = logging.getLogger(__name__)


# logger.setLevel(logging.DEBUG)


def raw(m, key, default=0.0):
    try:
        return m[key]['raw']
    except:
        pass

    return default


def fmt(m, key, default=0.0):
    try:
        return m[key]['fmt']
    except:
        pass

    return default


def cookie(name, value):
    return cookiejar.Cookie(version=0, name=name, value=value,
                            port=None, port_specified=False, domain=".yahoo.com", domain_specified=True,
                            domain_initial_dot=True, path="/", path_specified=True, secure=True, expires=None,
                            discard=False, comment=None, comment_url=None, rest=dict())


class Yahoo(BaseClient):
    def __init__(self, ctx):
        super().__init__()

        self.crumb = None
        self.realtime = {}
        self.historicdata = {}
        self.js = jsonParser.jsonObject

    def _read_ticker_csv_file(self, ticker):

        fn = os.path.join(self.basedir, 'yahoo-{}.csv'.format(ticker))

        if not os.path.isfile(fn):
            return

        with open(fn, newline='', encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)

            ticks = {}

            for row in reader:
                tick  = self.get_ticker()
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

        :param ticker: the ticker symbol e.g. VOD.L
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

        cookies = [cookie("maex","%7B%22v2%22%3A%7B%7D%7D"),
                   cookie("EuConsent", "CPZ7-cAPZ7-cAAOACBENCRCoAP_AAH_AACiQIlNd_X__bX9n-_7_7ft0cY1f9_r3r-QzjgfNs-8F3L_W_L0X32E7NF36pq4KuR4ku3bBIQFtHMnUTUmxaolVrzHsak2cpyNKI7LkknsZe2dYGH9Pn9lD-YKZ7_5___f53T___9_-39z3_9f___d9_-__-vjfV599n_v9fV_7_9nf_____-_-___4IQQ_AJMNS8gC7EscGTSMIoQQIwrCQqAUAFFAMLRFYAODgp2VgEuoIWACAVARgRAgxBRgwCAAACAJCIgJACwQCIAiAQAAgARAIQAETAILACwMAgAFANCxACgAECQgyICI5TAgIkSiglsrEEoK9jTCAOssAKBRGRUACJAAASAgJCwcxwBICXCyQJMULwAw0AGAAIIlCIAMAAQRKFQAYAAgiUA"),
                   cookie("GUCS", "AR0nzQVM"),
                   cookie("GUC", "AQABBwFimlxjZUIcxQRM"),
                   cookie("PRF","t%3DVFIAX"),
                   cookie("thamba","1"),
                   cookie("A1", "d=AQABBNAVmWICEEFBM1xh-RmAmPpJJIsAz3YFEgABBwFcmmJlY_bPb2UB9iMAAAcIzhWZYm7SAIg&S=AQAAAucqV1HMdCsRf6key1gdaFs"),
                   cookie("A1S", "d=AQABBNAVmWICEEFBM1xh-RmAmPpJJIsAz3YFEgABBwFcmmJlY_bPb2UB9iMAAAcIzhWZYm7SAIg&S=AQAAAucqV1HMdCsRf6key1gdaFs&j=GDPR"),
                   cookie("A3", "d=AQABBNAVmWICEEFBM1xh-RmAmPpJJIsAz3YFEgABBwFcmmJlY_bPb2UB9iMAAAcIzhWZYm7SAIg&S=AQAAAucqV1HMdCsRf6key1gdaFs")
                   ]

        try:
            text = self.urlopen(url, redirect=True, data=None, headers=None, cookies=cookies)
        except BaseException as e:
            logger.exception("BaseException ticker=%s datacode=%s", ticker, datacode)
            return 'Yahoo.getRealtime({}, {}) - urlopen: {}'.format(ticker, datacode, e)

        try:
            with open(os.path.join(self.basedir, 'yahoo-{}.html'.format(ticker)), "w", encoding="utf-8") as text_file:
                print(f"<!-- '{url}' -->\r\n\r\n{text}", file=text_file)
        except BaseException:
            logger.exception("BaseException ticker=%s datacode=%s", ticker, datacode)

        try:
            text = urllib.parse.unquote(text)
            text = text.replace('\\u002F', '/')

            r = '"CrumbStore":{"crumb":"([^"]{11})"'
            pattern = re.compile(r)
            match = pattern.search(text)

            if  match:
                self.crumb = match.group(1)

        except BaseException as e:
            logger.exception("BaseException ticker=%s datacode=%s", ticker, datacode)
            return 'Yahoo.getRealtime({}, {}) - crumb: {}'.format(ticker, datacode, e)

        try:
            start = text.find('"QuoteSummaryStore":{')

            if start < 0:
                return None

            start = start + len('"QuoteSummaryStore":')
            results = self.js.parseString(text[start:])

            if not results:
                return None

        except BaseException as e:
            logger.exception("BaseException ticker=%s datacode=%s", ticker, datacode)
            return 'Yahoo.getRealtime({}, {}) - parsing: {}'.format(ticker, datacode, e)

        with open(os.path.join(self.basedir, 'yahoo-{}.js'.format(ticker)), "w", encoding="utf-8") as text_file:
            print(f"// '{url}' QuoteSummaryStore:\n", file=text_file)
            pprint.pprint(results.asList(), stream=text_file)

        try:
            price = results['price']
            quoteType = results['quoteType']
            summaryDetail = results['summaryDetail']
            defaultKeyStatistics = results['defaultKeyStatistics'] if 'defaultKeyStatistics' in results else dict()

            if not price:
                return 'Could not find price for \'{}\''.format(ticker)

            if ticker not in self.realtime:
                self.realtime[ticker] =  self.get_ticker()

            tick = self.realtime[ticker]

            tick[Datacode.TIMESTAMP] = time.time()

            tick[Datacode.PREV_CLOSE] = float(raw(price, 'regularMarketPreviousClose'))
            tick[Datacode.OPEN] = float(raw(price, 'regularMarketOpen'))
            tick[Datacode.CHANGE] = float(raw(price, 'regularMarketChange'))
            tick[Datacode.CHANGE_IN_PERCENT] = 100 * float(raw(price, 'regularMarketChangePercent'))
            tick[Datacode.LOW] = float(raw(price, 'regularMarketDayLow'))
            tick[Datacode.HIGH] = float(raw(price, 'regularMarketDayHigh'))
            tick[Datacode.LAST_PRICE] = float(raw(price, 'regularMarketPrice'))
            tick[Datacode.VOLUME] = float(raw(price, 'regularMarketVolume'))
            tick[Datacode.AVG_DAILY_VOL_3MONTH] = float(raw(price, 'averageDailyVolume3Month'))
            tick[Datacode.BETA] = float(raw(summaryDetail, 'beta'))
            tick[Datacode.EPS] = self.save_wrapper(lambda: float(raw(results['defaultKeyStatistics'], 'trailingEps')))
            tick[Datacode.PE_RATIO] = float(raw(summaryDetail, 'trailingPE'))
            tick[Datacode.DIV] = float(raw(summaryDetail, 'dividendRate'))
            tick[Datacode.DIV_YIELD] = float(raw(summaryDetail, 'dividendYield'))
            tick[Datacode.EX_DIV_DATE] = self.save_wrapper(
                lambda: dateutil.parser.parse(str(fmt(summaryDetail, 'exDividendDate')), yearfirst=True, dayfirst=False).date())
            tick[Datacode.SHARES_OUT] = float(raw(defaultKeyStatistics, 'sharesOutstanding'))
            tick[Datacode.FREE_FLOAT] = float(raw(defaultKeyStatistics, 'floatShares'))

            tick[Datacode.PAYOUT_RATIO] = float(raw(summaryDetail, 'payoutRatio'))
            tick[Datacode.LOW_52_WEEK] = float(raw(summaryDetail, 'fiftyTwoWeekLow'))
            tick[Datacode.HIGH_52_WEEK] = float(raw(summaryDetail, 'fiftyTwoWeekHigh'))
            tick[Datacode.MARKET_CAP] = float(raw(summaryDetail, 'marketCap'))

            tick[Datacode.BID] = float(raw(summaryDetail, 'bid'))
            tick[Datacode.ASK] = float(raw(summaryDetail, 'ask'))
            tick[Datacode.BIDSIZE] = float(raw(summaryDetail, 'bidSize'))
            tick[Datacode.ASKSIZE] = float(raw(summaryDetail, 'askSize'))

            tick[Datacode.EXPIRY_DATE] = self.save_wrapper(
                lambda: dateutil.parser.parse(str(fmt(summaryDetail, 'expireDate')), yearfirst=True, dayfirst=False).date())

            if quoteType:
                t = int(price['regularMarketTime'])
                tz = pytz.timezone(quoteType['exchangeTimezoneName'])

                tick[Datacode.TIMEZONE] = tz
                dt = datetime.datetime.fromtimestamp(t, tz)

                tick[Datacode.LAST_PRICE_DATE] = dt.date()
                tick[Datacode.LAST_PRICE_TIME] = dt.time()

            tick[Datacode.TICKER] = self.save_wrapper(lambda: str(price['symbol']))
            tick[Datacode.EXCHANGE] = self.save_wrapper(lambda: str(price['exchange']))
            tick[Datacode.CURRENCY] = self.save_wrapper(lambda: str(price['currency']))

            # some Moscow symbols miss currency in data block but show it in text e.g. VTBBA.ME, TBIOA.ME
            if not tick[Datacode.CURRENCY]:
                r = r'Currency in ([A-Z]{3})\b'
                match = re.compile(r, flags=re.DOTALL).search(text)
                if match:
                    tick[Datacode.CURRENCY] = match.group(1)

            # fallback for yield on US mutual funds and ETFs, which is in different field
            if not tick[Datacode.DIV_YIELD]:
                tick[Datacode.DIV_YIELD] = float(raw(summaryDetail, 'yield'))

            name = price['longName'] or price['shortName']
            if name:
                tick[Datacode.NAME] = html.unescape(str(name))
            else:
                tick[Datacode.NAME] = tick[Datacode.TICKER]

            tick[Datacode.SECTOR] = self.save_wrapper(lambda: str(results['summaryProfile']['sector']))
            tick[Datacode.INDUSTRY] = self.save_wrapper(lambda: str(results['summaryProfile']['industry']))

        except BaseException as e:
            logger.exception("BaseException ticker=%s datacode=%s", ticker, datacode)
            return 'Yahoo.getRealtime({}, {}) - process: {}'.format(ticker, datacode, e)

        return self._return_value(self.realtime[ticker], datacode)

    def getHistoric(self, ticker: str, datacode: int, date):

        """
        Retrieve historic data for ticker from Yahoo Finance and cache it for further lookups

        :param ticker: the ticker symbol e.g. VOD.L
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

        try:
            date_as_dt = dateutil.parser.parse(date, yearfirst=True, dayfirst=False)
        except BaseException as e:
            logger.exception("BaseException ticker=%s datacode=%s", ticker, datacode)
            return 'Yahoo.getHistoric({}, {}, {}) - date_as_dt: {}'.format(ticker, datacode, date, e)

        if ticker in self.historicdata:
            ticks = self.historicdata[ticker]

            if date in ticks:
                return self._return_value(ticks[date], datacode)

            # weekend, trading holiday or as yet un-fetched
            if min(ticks) <= date <= max(ticks):
                return 'Not a trading day \'{}\''.format(date)

            # (potentially) future date
            if date > max(ticks):
                t1 = int(date_as_dt.timestamp())
                t2 = int(time.time())
                if t1 > t2:
                    return 'Future date \'{}\''.format(date)

                min_tick_date = int(dateutil.parser.parse(min(ticks), yearfirst=True, dayfirst=False).timestamp())  # remember current earliest date

        if not self.crumb:
            self.getRealtime(ticker, datacode)

        if not self.crumb:
            return 'Yahoo.getHistoric({}, {}, {}) - crumb'.format(ticker, datacode, date)

        try:
            t1 = int(date_as_dt.timestamp())
            t2 = int(time.time())

            if min_tick_date:
                t1 = min_tick_date

            if t1 >= t2:
                return 'Future date \'{}\''.format(date)

            if t1 < int(dateutil.parser.parse('2000-01-01', yearfirst=True, dayfirst=False).timestamp()):
                return 'Date before 2000 \'{}\''.format(date)

            t1 = t1 - 2682000  # pad with extra month

        except BaseException as e:
            logger.exception("BaseException ticker=%s datacode=%s", ticker, datacode)
            return 'Yahoo.getHistoric({}, {}, {}) - date: {}'.format(ticker, datacode, date, e)

        try:

            url = 'https://query1.finance.yahoo.com/v7/finance/download/{}' \
                  '?period1={}&period2={}&interval=1d&events=history&crumb={}' \
                .format(ticker, t1, t2, urllib.parse.quote_plus(self.crumb))

            text = self.urlopen(url)

            with open(os.path.join(self.basedir, 'yahoo-{}.csv'.format(ticker)), "w", encoding="utf-8") as csv_file:
                print(text, file=csv_file)

            self._read_ticker_csv_file(ticker)

        except HttpException:
            logger.exception("HttpException ticker=%s datacode=%s date=%s", ticker, datacode, date)
            return None

        except BaseException as e:
            logger.exception("BaseException ticker=%s datacode=%s date=%s", ticker, datacode, date)
            return 'Yahoo.getHistoric({}, {}, {}) - urlopen: {}'.format(ticker, datacode, date, e)

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
            logger.exception("BaseException ticker=%s datacode=%s", ticker, datacode)
            return 'Yahoo.getHistoric({}, {}, {}) - process: {}'.format(ticker, datacode, date, e)

        return None


def createInstance(ctx):
    return Yahoo(ctx)
