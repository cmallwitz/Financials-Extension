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
from naivehtmlparser import NaiveHTMLParser

logger = logging.getLogger(__name__)


# logger.setLevel(logging.DEBUG)


def handle_abbreviations(s):
    s = str(s).strip()
    if s.endswith('M'):
        return float(s[:-1]) * 1000000
    elif s.endswith('B'):
        return float(s[:-1]) * 1000000000
    elif s.endswith('T'):
        return float(s[:-1]) * 1000000000000
    return float(s)

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

        if ticker not in self.realtime:
            self.realtime[ticker] = self.get_ticker()

        tick = self.realtime[ticker]

        url = 'https://finance.yahoo.com/quote/{}?p={}'.format(ticker, ticker)

        cookies = [
            cookie("A1", "d=AQABBDcIZWMCEHYhFYqQ7qyTvvD2eAT87mcFEgABCAGDlGPBY_bPb2UB9qMAAAcILwhlY6iIogg&S=AQAAAjZvTuAn1nH4h71eKJtCEHk"),
            cookie("A1S", "d=AQABBDcIZWMCEHYhFYqQ7qyTvvD2eAT87mcFEgABCAGDlGPBY_bPb2UB9qMAAAcILwhlY6iIogg&S=AQAAAjZvTuAn1nH4h71eKJtCEHk&j=GDPR"),
            cookie("A3", "d=AQABBDcIZWMCEHYhFYqQ7qyTvvD2eAT87mcFEgABCAGDlGPBY_bPb2UB9qMAAAcILwhlY6iIogg&S=AQAAAjZvTuAn1nH4h71eKJtCEHk"),
            cookie("GUC", "AQABCAFjlINjwUIcFQQQ&s=AQAAAFOQKXn7&g=Y5M5Jg"),
            cookie("GUCS", "ASHFadZS"),
            cookie("maex", "{\"v2\":{}}"),
            cookie("PRF", "t=TQQQ%2BASTO.L%2BCHMI%2BVFIAX%2BIBM%2BXMR-USD%2BMVV%2BSECU-B.ST%2BMSFT"),
            cookie("thamba", "1")
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
            r = '"crumb":"([^"]{11})"'
            pattern = re.compile(r)
            match = pattern.search(text)

            if  match:
                self.crumb = match.group(1)

        except BaseException as e:
            logger.exception("BaseException ticker=%s datacode=%s", ticker, datacode)
            return 'Yahoo.getRealtime({}, {}) - crumb: {}'.format(ticker, datacode, e)

        tick[Datacode.TIMESTAMP] = time.time()

        try:
            parser = NaiveHTMLParser()
            root = parser.feed(text)
            parser.close()

        except BaseException as e:
            logger.exception("BaseException ticker=%s datacode=%s", ticker, datacode)
            return 'Yahoo.getRealtime({}, {}) - HTML parsing: {}'.format(ticker, datacode, e)

        try:
            parsed = {}

            found = root.findall(f".//fin-streamer[@data-symbol='{ticker}']")
            for d in found:
                if hasattr(d, 'attrib') and 'data-field' in d.attrib and 'value' in d.attrib:
                    parsed[d.attrib['data-field']] = d.attrib['value'].replace('−', '-').replace(',', '').strip()

            found = root.findall(f".//td[@data-test]")
            for d in found:
                if d:
                    span = d.find('./span')
                    if hasattr(span, 'text') and span.text is not None:
                        parsed[d.attrib['data-test']] = span.text.replace('−', '-').replace(',', '').strip()
                else:
                    if hasattr(d, 'attrib') and hasattr(d, 'text'):
                        parsed[d.attrib['data-test']] = d.text.replace('−', '-').replace(',', '').strip()

            if 'regularMarketPrice' not in parsed:
                return None

            tick[Datacode.PREV_CLOSE] = self.save_wrapper(lambda: float(parsed['PREV_CLOSE-value']))
            tick[Datacode.OPEN] = self.save_wrapper(lambda: float(parsed['OPEN-value']))
            tick[Datacode.CHANGE] = self.save_wrapper(lambda: float(parsed['regularMarketChange']))
            tick[Datacode.CHANGE_IN_PERCENT] = self.save_wrapper(lambda: float(parsed['regularMarketChangePercent']))

            t = parsed['DAYS_RANGE-value'] if 'DAYS_RANGE-value'  in parsed else ''
            t = t.split(' - ')
            tick[Datacode.LOW] = self.save_wrapper(lambda: float(t[0]))
            tick[Datacode.HIGH] = self.save_wrapper(lambda: float(t[1]))

            tick[Datacode.LAST_PRICE] = self.save_wrapper(lambda: float(parsed['regularMarketPrice']))
            tick[Datacode.VOLUME] = self.save_wrapper(lambda: float(parsed['regularMarketVolume']))
            tick[Datacode.AVG_DAILY_VOL_3MONTH] = self.save_wrapper(lambda: float(parsed['AVERAGE_VOLUME_3MONTH-value']))
            tick[Datacode.BETA] = self.save_wrapper(lambda: float(parsed['BETA_5Y-value']))
            tick[Datacode.EPS] = self.save_wrapper(lambda: float(parsed['EPS_RATIO-value']))
            tick[Datacode.PE_RATIO] = self.save_wrapper(lambda: float(parsed['PE_RATIO-value']))

            t = parsed['DIVIDEND_AND_YIELD-value'] if 'DIVIDEND_AND_YIELD-value' in parsed else ''
            t = t.replace('(', '').replace(')', '').replace('%', '').strip().split(' ')
            tick[Datacode.DIV] = self.save_wrapper(lambda: float(t[0]))
            tick[Datacode.DIV_YIELD] = self.save_wrapper(lambda: float(t[1])/100.0)

            tick[Datacode.EX_DIV_DATE] = self.save_wrapper(
                lambda: dateutil.parser.parse(str(parsed['EX_DIVIDEND_DATE-value']), yearfirst=True, dayfirst=False).date())

            # https://finance.yahoo.com/quote/IBM/key-statistics?p=IBM
            # tick[Datacode.SHARES_OUT] = float(raw(defaultKeyStatistics, 'sharesOutstanding'))
            # tick[Datacode.FREE_FLOAT] = float(raw(defaultKeyStatistics, 'floatShares'))
            # tick[Datacode.PAYOUT_RATIO] = float(raw(summaryDetail, 'payoutRatio'))

            t = parsed['FIFTY_TWO_WK_RANGE-value'] if 'FIFTY_TWO_WK_RANGE-value' in parsed else ''
            t = t.split(' - ')
            tick[Datacode.LOW_52_WEEK] = self.save_wrapper(lambda: float(t[0]))
            tick[Datacode.HIGH_52_WEEK] = self.save_wrapper(lambda: float(t[1]))

            tick[Datacode.MARKET_CAP] = self.save_wrapper(lambda: float(handle_abbreviations(parsed['MARKET_CAP-value'])))

            t = parsed['BID-value'] if 'BID-value' in parsed else ''
            t = t.split(' x ')
            tick[Datacode.BID] = self.save_wrapper(lambda: float(t[0]))
            tick[Datacode.BIDSIZE] = self.save_wrapper(lambda: float(t[1]))

            t = parsed['ASK-value'] if 'ASK-value' in parsed else ''
            t = t.split(' x ')
            tick[Datacode.ASK] = self.save_wrapper(lambda: float(t[0]))
            tick[Datacode.ASKSIZE] = self.save_wrapper(lambda: float(t[1]))

            tick[Datacode.EXPIRY_DATE] = self.save_wrapper(
                lambda: dateutil.parser.parse(str(parsed['EXPIRE_DATE-value']), yearfirst=True, dayfirst=False).date())

            r = '<div id="quote-market-notice"[^>]*><span>([^>]*)</span></div>'
            match = re.compile(r, flags=re.DOTALL).search(text)
            if match:
                t = html.unescape(match.group(1)).strip().split(' ')
                tick[Datacode.TIMEZONE] = self.save_wrapper(lambda: pytz.timezone(t[-1]))

            # if quoteType:
            #     t = int(price['regularMarketTime'])
            #     tz = pytz.timezone(quoteType['exchangeTimezoneName'])
            #
            #     tick[Datacode.TIMEZONE] = tz
            #     dt = datetime.datetime.fromtimestamp(t, tz)
            #
            #     tick[Datacode.LAST_PRICE_DATE] = dt.date()
            #     tick[Datacode.LAST_PRICE_TIME] = dt.time()

            tick[Datacode.TICKER] = ticker

            r = '<span>(\\w+?) - [^>]*Currency in ([\\w]+)[^>]*</span>'
            match = re.compile(r, flags=re.DOTALL).search(text)
            if match:
                tick[Datacode.EXCHANGE] = self.save_wrapper(lambda: html.unescape(match.group(1)).strip())
                tick[Datacode.CURRENCY] = self.save_wrapper(lambda: html.unescape(match.group(2)).strip())

            # fallback for yield on US mutual funds and ETFs, which is in different field
            if not tick[Datacode.DIV_YIELD]:
                tick[Datacode.DIV_YIELD] = self.save_wrapper(lambda: float(parsed['LAST_DIVIDEND-value']))

            tick[Datacode.NAME] = self.save_wrapper(
                lambda: html.unescape(root.find('.//h1').text).strip())

            if not tick[Datacode.NAME]:
                tick[Datacode.NAME] = tick[Datacode.TICKER]

            # https://finance.yahoo.com/quote/IBM/profile?p=IBM
            # tick[Datacode.SECTOR] = self.save_wrapper(lambda: str(results['summaryProfile']['sector']))
            # tick[Datacode.INDUSTRY] = self.save_wrapper(lambda: str(results['summaryProfile']['industry']))

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
            return 'Yahoo.getHistoric({}, {}, {}) - crumb missing'.format(ticker, datacode, date)

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
