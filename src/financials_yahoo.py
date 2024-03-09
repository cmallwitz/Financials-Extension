#  financials_yahoo.py
#
#  license: GNU LGPL
#
#  This library is free software; you can redistribute it and/or
#  modify it under the terms of the GNU Lesser General Public
#  License as published by the Free Software Foundation; either
#  version 3 of the License, or (at your option) any later version.


import csv
import html
import logging
import os
import re
import time
import urllib.parse

import dateutil.parser

import jsonParser
from baseclient import BaseClient, HttpException
from datacode import Datacode
from naivehtmlparser import NaiveHTMLParser

logger = logging.getLogger(__name__)


# logger.setLevel(logging.DEBUG)


def default(obj, prop, fallback=''):
    try:
        if obj is None or property is None:
            return fallback

        v = None
        if hasattr(obj, prop):
            v = getattr(obj, prop)
        elif prop in obj:
            v = obj[prop]
        return v if v is not None else fallback
    except:
        pass
    return fallback


def handle_abbreviations(s):
    s = str(s).strip()
    if s.endswith('M'):
        return float(s[:-1]) * 1000000
    elif s.endswith('B'):
        return float(s[:-1]) * 1000000000
    elif s.endswith('T'):
        return float(s[:-1]) * 1000000000000
    return float(s)


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
                tick = self.get_ticker()
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

        needStatistics = datacode in [Datacode.SHARES_OUT.value, Datacode.FREE_FLOAT.value, Datacode.PAYOUT_RATIO.value]
        needProfile = datacode in [Datacode.SECTOR.value, Datacode.INDUSTRY.value]

        # use cached value for up to 60 seconds
        if ticker in self.realtime:
            tick = self.realtime[ticker]
            if Datacode.TIMESTAMP in tick and type(tick[Datacode.TIMESTAMP]) == float and time.time() - 60 < tick[Datacode.TIMESTAMP]:
                if (tick[Datacode.YAHOO_STATISTIC_RECEIVED] or not needStatistics) and (
                        tick[Datacode.YAHOO_PROFILE_RECEIVED] or not needProfile) and (
                        tick[Datacode.YAHOO_SUMMARY_RECEIVED]):
                    return self._return_value(tick, datacode)
            else:
                del self.realtime[ticker]

        if ticker not in self.realtime:
            self.realtime[ticker] = self.get_ticker()

        if needStatistics:
            return self.getRealtimeStatistics(ticker, datacode)

        if needProfile:
            return self.getRealtimeProfile(ticker, datacode)

        return self.getRealtimeSummary(ticker, datacode)

    def getData(self, url, ticker, datacode, html_file):

        try:
            text = self.urlopen(url, redirect=True)
        except BaseException as e:
            logger.exception("BaseException (1) ticker=%s datacode=%s last_url=%s redirect_count=%s %s",
                             ticker, datacode, self.last_url, self.redirect_count, e)
            return None

        try:
            with open(os.path.join(self.basedir, html_file), "w", encoding="utf-8") as text_file:
                print(f"<!-- '{self.last_url}' -->\r\n\r\n{text}", file=text_file)
        except BaseException as e:
            logger.exception("BaseException (2) ticker=%s datacode=%s %s", ticker, datacode, e)

        if not text:
            return None

        try:
            parser = NaiveHTMLParser()
            root = parser.feed(text)
            parser.close()
        except BaseException as e:
            logger.exception("BaseException (3) ticker=%s datacode=%s - HTML parsing - %s", ticker, datacode, e)
            return None

        form = root.find(f".//form[@class='consent-form']")

        if form:
            inputs = form.findall(f".//input")

            if inputs:

                data = {'reject': 'reject'}
                for d in inputs:
                    data[d.attrib['name']] = d.attrib['value']

                try:
                    text = self.urlopen(self.last_url, redirect=True, data=urllib.parse.urlencode(data))
                except BaseException as e:
                    logger.exception("BaseException (4) ticker=%s datacode=%s last_url=%s redirect_count=%s %s",
                                     ticker, datacode, self.last_url, self.redirect_count, e)

        return text

    def getRealtimeSummary(self, ticker, datacode):

        """
        Retrieve realtime data from Yahoo Finance - Summary tab
        """

        tick = self.realtime[ticker]

        url = 'https://finance.yahoo.com/quote/{}?p={}'.format(ticker, ticker)
        text = self.getData(url, ticker, datacode, f'yahoo-{ticker}.html')

        if text is None:
            del self.realtime[ticker]
            return 'Yahoo.getRealtimeSummary({}, {}) - getData'.format(ticker, datacode)

        try:
            r = '"crumb":"([^"]{11})"'
            pattern = re.compile(r)
            match = pattern.search(text)
            if match:
                self.crumb = match.group(1)
        except BaseException as e:
            logger.exception("BaseException ticker=%s datacode=%s", ticker, datacode)
            del self.realtime[ticker]
            return 'Yahoo.getRealtimeSummary({}, {}) - crumb: {}'.format(ticker, datacode, e)

        try:
            parser = NaiveHTMLParser()
            root = parser.feed(text)
            parser.close()
        except BaseException as e:
            logger.exception("BaseException ticker=%s datacode=%s", ticker, datacode)
            return 'Yahoo.getRealtimeSummary({}, {}) - HTML parsing: {}'.format(ticker, datacode, e)

        try:
            if not root:
                logger.exception("BaseException ticker=%s datacode=%s", ticker, datacode)
                return 'Yahoo.getRealtimeSummary({}, {}) - root missing'.format(ticker, datacode)

            tick[Datacode.TICKER] = ticker
            tick[Datacode.TIMESTAMP] = time.time()
            tick[Datacode.YAHOO_SUMMARY_RECEIVED] = True

            parsed = {}

            found = root.findall(f".//fin-streamer[@data-symbol='{ticker}']")
            for d in found:
                if hasattr(d, 'attrib') and 'data-field' in d.attrib:
                    value = default(d.attrib, 'value') or default(d.attrib, 'data-value')
                    parsed[d.attrib['data-field']] = value.replace('−', '-').replace(',', '').strip()

            # for futures "regularMarketVolume" is from actual future ticker (potentially different to requested one)
            if 'regularMarketVolume' not in parsed:
                found = root.findall(f".//fin-streamer[@data-field='regularMarketVolume']")
                for d in found:
                    if hasattr(d, 'attrib') and 'data-field' in d.attrib and 'data-symbol' in d.attrib:
                        value = default(d.attrib, 'value') or default(d.attrib, 'data-value')
                        parsed[d.attrib['data-field']] = value.replace('−', '-').replace(',', '').strip()
                        tick[Datacode.TICKER] = default(d.attrib, 'data-symbol').strip()

            found = root.findall(f".//td[@data-test]")
            for d in found:
                if d:
                    span = d.find('./span')
                    if hasattr(d, 'attrib') and hasattr(span, 'text'):
                        parsed[d.attrib['data-test']] = default(span, 'text').replace('−', '-').replace(',', '').strip()
                else:
                    if hasattr(d, 'attrib') and hasattr(d, 'text'):
                        parsed[d.attrib['data-test']] = default(d, 'text').replace('−', '-').replace(',', '').strip()

            if 'regularMarketPrice' not in parsed:
                return None

            tick[Datacode.PREV_CLOSE] = self.save_wrapper(lambda: float(parsed['PREV_CLOSE-value']))
            tick[Datacode.OPEN] = self.save_wrapper(lambda: float(parsed['OPEN-value']))
            tick[Datacode.CHANGE] = self.save_wrapper(lambda: float(parsed['regularMarketChange']))
            tick[Datacode.CHANGE_IN_PERCENT] = self.save_wrapper(lambda: float(parsed['regularMarketChangePercent']))

            t = default(parsed, 'DAYS_RANGE-value').split(' - ')
            tick[Datacode.LOW] = self.save_wrapper(lambda: float(t[0]))
            tick[Datacode.HIGH] = self.save_wrapper(lambda: float(t[1]))

            tick[Datacode.LAST_PRICE] = self.save_wrapper(lambda: float(parsed['regularMarketPrice']))
            tick[Datacode.VOLUME] = self.save_wrapper(lambda: float(parsed['regularMarketVolume']))
            tick[Datacode.AVG_DAILY_VOL_3MONTH] = self.save_wrapper(lambda: float(parsed['AVERAGE_VOLUME_3MONTH-value']))
            tick[Datacode.BETA] = self.save_wrapper(lambda: float(parsed['BETA_5Y-value']))
            tick[Datacode.EPS] = self.save_wrapper(lambda: float(parsed['EPS_RATIO-value']))
            tick[Datacode.PE_RATIO] = self.save_wrapper(lambda: float(parsed['PE_RATIO-value']))

            t = default(parsed, 'DIVIDEND_AND_YIELD-value').replace('(', '').replace(')', '').replace('%', '').strip().split(' ')
            tick[Datacode.DIV] = self.save_wrapper(lambda: float(t[0]))
            tick[Datacode.DIV_YIELD] = self.save_wrapper(lambda: float(t[1])/100.0)

            tick[Datacode.EX_DIV_DATE] = self.save_wrapper(
                lambda: dateutil.parser.parse(parsed['EX_DIVIDEND_DATE-value'], yearfirst=True, dayfirst=False).date())

            t = default(parsed, 'FIFTY_TWO_WK_RANGE-value').split(' - ')
            tick[Datacode.LOW_52_WEEK] = self.save_wrapper(lambda: float(t[0]))
            tick[Datacode.HIGH_52_WEEK] = self.save_wrapper(lambda: float(t[1]))

            tick[Datacode.MARKET_CAP] = self.save_wrapper(lambda: float(handle_abbreviations(parsed['MARKET_CAP-value'])))

            t = default(parsed, 'BID-value').split(' x ')
            tick[Datacode.BID] = self.save_wrapper(lambda: float(t[0]))
            tick[Datacode.BIDSIZE] = self.save_wrapper(lambda: float(t[1]))

            t = default(parsed, 'ASK-value').split(' x ')
            tick[Datacode.ASK] = self.save_wrapper(lambda: float(t[0]))
            tick[Datacode.ASKSIZE] = self.save_wrapper(lambda: float(t[1]))

            tick[Datacode.EXPIRY_DATE] = self.save_wrapper(
                lambda: dateutil.parser.parse(parsed['EXPIRE_DATE-value'], yearfirst=True, dayfirst=False).date())

            tick[Datacode.SETTLEMENT_DATE] = self.save_wrapper(
                lambda: dateutil.parser.parse(parsed['SETTLEMENT_DATE-value'], yearfirst=True, dayfirst=False).date())

            r = '<div id="quote-market-notice"[^>]*><span>([^>]*?)(. Market open.)?</span></div>'
            match = re.compile(r, flags=re.DOTALL).search(text)
            if match:
                t = html.unescape(match.group(1)).strip().split(' ')
                tick[Datacode.TIMEZONE] = self.save_wrapper(lambda: t[-1])

            # if quoteType:
            #     t = int(price['regularMarketTime'])
            #     tz = pytz.timezone(quoteType['exchangeTimezoneName'])
            #
            #     tick[Datacode.TIMEZONE] = tz
            #     dt = datetime.datetime.fromtimestamp(t, tz)
            #
            #     tick[Datacode.LAST_PRICE_DATE] = dt.date()
            #     tick[Datacode.LAST_PRICE_TIME] = dt.time()

            r = '<span>([ \\w]+?) - [^>]*Currency in ([\\w]+)[^>]*</span>'
            match = re.compile(r, flags=re.DOTALL).search(text)
            if match:
                tick[Datacode.EXCHANGE] = self.save_wrapper(lambda: html.unescape(match.group(1)).strip())
                tick[Datacode.CURRENCY] = self.save_wrapper(lambda: html.unescape(match.group(2)).strip())

            # fallback for dividend/yield on mutual funds and ETFs
            if not tick[Datacode.DIV]:
                tick[Datacode.DIV] = self.save_wrapper(lambda: float(parsed['LAST_DIVIDEND-value']))
            if not tick[Datacode.DIV_YIELD]:
                tick[Datacode.DIV_YIELD] = self.save_wrapper(lambda: float(parsed['TD_YIELD-value'].replace('%', '').strip())/100.0)

            tick[Datacode.NAME] = self.save_wrapper(
                lambda: html.unescape(root.find('.//h1').text).strip())

            if not tick[Datacode.NAME]:
                tick[Datacode.NAME] = tick[Datacode.TICKER]

        except BaseException as e:
            logger.exception("BaseException ticker=%s datacode=%s", ticker, datacode)
            del self.realtime[ticker]
            return 'Yahoo.getRealtimeSummary({}, {}) - process: {}'.format(ticker, datacode, e)

        return self._return_value(self.realtime[ticker], datacode)

    def getRealtimeStatistics(self, ticker, datacode):

        """
        Retrieve realtime data from Yahoo Finance - Statistics tab
        """

        tick = self.realtime[ticker]

        url = 'https://finance.yahoo.com/quote/{}/key-statistics?p={}'.format(ticker, ticker)
        text = self.getData(url, ticker, datacode, f'yahoo-{ticker}-statistics.html')

        if text is None:
            del self.realtime[ticker]
            return 'Yahoo.getRealtimeStatistics({}, {}) - getData'.format(ticker, datacode)

        try:
            parser = NaiveHTMLParser()
            root = parser.feed(text)
            parser.close()
        except BaseException as e:
            logger.exception("BaseException ticker=%s datacode=%s", ticker, datacode)
            del self.realtime[ticker]
            return 'Yahoo.getRealtimeStatistics({}, {}) - HTML parsing: {}'.format(ticker, datacode, e)

        statistics = root.find(".//section[@data-test='qsp-statistics']")

        tick[Datacode.TICKER] = ticker
        tick[Datacode.TIMESTAMP] = time.time()
        tick[Datacode.YAHOO_STATISTIC_RECEIVED] = True

        tick[Datacode.SHARES_OUT] = None
        tick[Datacode.FREE_FLOAT] = None
        tick[Datacode.PAYOUT_RATIO] = None

        if statistics is None:
            return None

        parsed = {}

        try:

            # Valuation Measures
            found = statistics.find('./div[2]/div[1]//table')
            if found:
                for d in found.findall('.//tr'):
                    key = d.find('./td[1]/span').text
                    if key is not None:
                        parsed[key] = d.find('./td[2]').text

            # Stock Price History
            found = statistics.find('./div[2]/div[2]/div[1]/div[1]//table')
            if found:
                for d in found.findall('.//tr'):
                    key = d.find('./td[1]/span').text
                    if key is not None:
                        parsed[key] = d.find('./td[2]').text

            # Share Statistics
            found = statistics.find('./div[2]/div[2]/div[1]/div[2]//table')
            if found:
                for d in found.findall('.//tr'):
                    key = d.find('./td[1]/span').text
                    if key is not None:
                        parsed[key] = d.find('./td[2]').text

            # Dividends & Splits
            found = statistics.find('./div[2]/div[2]/div[1]/div[3]//table')
            if found:
                for d in found.findall('.//tr'):
                    key = d.find('./td[1]/span').text
                    if key is not None:
                        parsed[key] = d.find('./td[2]').text

        except KeyError:
            pass

        tick[Datacode.SHARES_OUT] = self.save_wrapper(
            lambda: float(handle_abbreviations(parsed['Shares Outstanding'])))
        tick[Datacode.FREE_FLOAT] = self.save_wrapper(
            lambda: float(handle_abbreviations(parsed['Float'])))
        tick[Datacode.PAYOUT_RATIO] = self.save_wrapper(
            lambda: float(handle_abbreviations(parsed['Payout Ratio'].replace('%', '').strip()))/100.0)

        return self._return_value(self.realtime[ticker], datacode)

    def getRealtimeProfile(self, ticker, datacode):

        """
        Retrieve realtime data from Yahoo Finance - Profile tab
        """

        tick = self.realtime[ticker]

        url = 'https://finance.yahoo.com/quote/{}/profile?p={}'.format(ticker, ticker)
        text = self.getData(url, ticker, datacode, f'yahoo-{ticker}-profile.html')

        if text is None:
            del self.realtime[ticker]
            return 'Yahoo.getRealtimeProfile({}, {}) - getData'.format(ticker, datacode)

        try:
            parser = NaiveHTMLParser()
            root = parser.feed(text)
            parser.close()
        except BaseException as e:
            logger.exception("BaseException ticker=%s datacode=%s", ticker, datacode)
            del self.realtime[ticker]
            return 'Yahoo.getRealtimeProfile({}, {}) - HTML parsing: {}'.format(ticker, datacode, e)

        tick[Datacode.TICKER] = ticker
        tick[Datacode.TIMESTAMP] = time.time()
        tick[Datacode.YAHOO_PROFILE_RECEIVED] = True

        p = None

        if root:
            p = root.find(".//*[span='Sector(s)']")

        tick[Datacode.SECTOR] = self.save_wrapper(lambda: p.find("./span[2]").text)
        tick[Datacode.INDUSTRY] = self.save_wrapper(lambda: p.find("./span[4]").text)

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
            logger.exception("BaseException ticker=%s datacode=%s last_url=%s redirect_count=%s", ticker, datacode, self.last_url, self.redirect_count)
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
            self.getRealtime(ticker, Datacode.LAST_PRICE)

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
