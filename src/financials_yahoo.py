#  financials_yahoo.py
#
#  license: GNU LGPL
#
#  This library is free software; you can redistribute it and/or
#  modify it under the terms of the GNU Lesser General Public
#  License as published by the Free Software Foundation; either
#  version 3 of the License, or (at your option) any later version.


import datetime
import json
import logging
import os
import pytz
import re
import time
import urllib.parse

import dateutil.parser

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
        self.fetch_failures = {}  # ticker -> timestamp of last network failure

    def _read_ticker_json_file(self, ticker):

        fn = os.path.join(self.basedir, 'yahoo-hist-{}.json'.format(ticker))

        if not os.path.isfile(fn):
            return

        with open(fn, newline='', encoding="utf-8") as jsonfile:
            js = jsonfile.read()

        parsed = json.loads(js)
        parsed = parsed['chart']['result'][0]

        price_hint = 2
        if 'priceHint' in parsed['meta']:
            price_hint = str(parsed['meta']['priceHint'])
            if price_hint and price_hint.isnumeric():
                price_hint = int(price_hint)
            else:
                price_hint = 2

        tz = datetime.timezone(datetime.timedelta(seconds=parsed['meta']['gmtoffset']), parsed['meta']['exchangeTimezoneName'])

        rows = list(
            zip((datetime.datetime.fromtimestamp(ts, tz).date() for ts in parsed['timestamp']),
                parsed['indicators']['quote'][0]['open'],
                parsed['indicators']['quote'][0]['low'],
                parsed['indicators']['quote'][0]['high'],
                parsed['indicators']['quote'][0]['volume'],
                parsed['indicators']['quote'][0]['close'],
                parsed['indicators']['adjclose'][0]['adjclose']))

        ticks = {}

        for row in rows:
            tick = self.get_ticker()
            try:
                tick[Datacode.OPEN] = round(float(row[1]), price_hint)
                tick[Datacode.LOW] = round(float(row[2]), price_hint)
                tick[Datacode.HIGH] = round(float(row[3]), price_hint)
                tick[Datacode.VOLUME] = round(float(row[4]), price_hint)
                tick[Datacode.CLOSE] = round(float(row[5]), price_hint)
                tick[Datacode.ADJ_CLOSE] = round(float(row[6]), price_hint)
            except:
                pass

            if len(tick) > 0:
                ticks[str(row[0])] = tick  # Date

        self.historicdata[ticker] = ticks


    def handleCookiesAndConsent(self, url, ticker, datacode, html_file):

        try:
            text = self.urlopen(url)
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
                    if 'name' in d.attrib and 'value' in d.attrib:
                        data[d.attrib['name']] = d.attrib['value']

                try:
                    text = self.urlopen(self.last_url, data=data)
                except BaseException as e:
                    logger.exception("BaseException (4) ticker=%s datacode=%s last_url=%s redirect_count=%s %s",
                                     ticker, datacode, self.last_url, self.redirect_count, e)

                try:
                    with open(os.path.join(self.basedir, html_file), "w", encoding="utf-8") as text_file:
                        print(f"<!-- '{self.last_url}' (after consent handling) -->\r\n\r\n{text}", file=text_file)
                except BaseException as e:
                    logger.exception("BaseException (5) ticker=%s datacode=%s %s", ticker, datacode, e)

        return text

    def fetch_crumb(self):
        """Refreshes the crumb using the current session."""
        try:
            # Request fc.yahoo.com to obtain cookies bypassing EU consent redirect
            self.session.get("https://fc.yahoo.com", timeout=10)
            
            # Request crumb endpoint via query2
            response = self.session.get("https://query2.finance.yahoo.com/v1/test/getcrumb", timeout=10)
            
            if response.status_code == 200 and response.text and not response.text.startswith('{'):
                return response.text.strip()
            else:
                logger.warning("Crumb fetch returned HTTP %s: %s", response.status_code, response.text[:120] if response.text else '')
        except Exception as e:
            logger.error("Failed to fetch crumb: %s", e)
        return None

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
            if Datacode.TIMESTAMP in tick and type(tick[Datacode.TIMESTAMP]) == float and time.time() - 60 < tick[Datacode.TIMESTAMP]:
                return self._return_value(tick, datacode)
            else:
                del self.realtime[ticker]

        # Do not hammer Yahoo if network fetch failed recently for this ticker (60s backoff)
        if ticker in self.fetch_failures and (time.time() - self.fetch_failures[ticker]) < 60:
            return 'Yahoo rate-limited, retry later'

        if ticker not in self.realtime:
            self.realtime[ticker] = self.get_ticker()

        tick = self.realtime[ticker]

        if not self.crumb:
            new_crumb = self.fetch_crumb()
            if new_crumb:
                self.crumb = new_crumb
                logger.debug("Crumb successfully set: %s", self.crumb)
            else:
                del self.realtime[ticker]
                self.fetch_failures[ticker] = time.time()
                return 'Yahoo.getRealtime({}, {}) - failed to fetch crumb'.format(ticker, datacode)

        if not self.crumb:
            return 'Yahoo.getRealtime({}, {}) - crumb missing'.format(ticker, datacode)

        try:

            quoted_ticker = urllib.parse.quote(ticker, safe='')
            url = 'https://query1.finance.yahoo.com/v10/finance/quoteSummary/{}?formatted=true&' \
                  'modules=summaryProfile,financialData,quoteType,recommendationTrend,earnings,equityPerformance,summaryDetail,defaultKeyStatistics,calendarEvents,esgScores,price,pageViews,financialsTemplate&' \
                  'lang=en-US&region=US&crumb={}' \
                .format(quoted_ticker, urllib.parse.quote_plus(self.crumb))

            js = self.urlopen(url)

        except HttpException as e:
            logger.exception("HttpException querying ticker=%s datacode=%s", ticker, datacode)
            del self.realtime[ticker]
            self.fetch_failures[ticker] = time.time()
            return None

        except BaseException as e:
            logger.exception("BaseException querying ticker=%s datacode=%s", ticker, datacode)
            del self.realtime[ticker]
            self.fetch_failures[ticker] = time.time()
            return 'Yahoo.getRealtime({}, {}) - urlopen: {}'.format(ticker, datacode, e)

        try:

            with open(os.path.join(self.basedir, 'yahoo-{}.json'.format(ticker)), "w", encoding="utf-8") as json_file:
                print(f"<!-- '{self.last_url}' -->\r\n\r\n{js}", file=json_file)

            parsed = json.loads(js)
            parsed = parsed['quoteSummary']['result'][0]

            summaryDetail = dict()
            if 'summaryDetail' in parsed:
                summaryDetail = dict(sorted(parsed['summaryDetail'].items()))

            price = dict(sorted(parsed['price'].items()))

            if 'defaultKeyStatistics' in parsed:
                defaultKeyStatistics = dict(sorted(parsed['defaultKeyStatistics'].items()))
            else:
                defaultKeyStatistics = {}

            if 'summaryProfile' in parsed:
                summaryProfile = dict(sorted(parsed['summaryProfile'].items()))
            else:
                summaryProfile = {}

            quoteType = dict(sorted(parsed['quoteType'].items()))

        except BaseException as e:
            logger.exception("BaseException parsing ticker=%s datacode=%s", ticker, datacode)
            del self.realtime[ticker]
            return 'Yahoo.getRealtimeSummary({}, {}) - exception: {}'.format(ticker, datacode, e)

        try:

            tick[Datacode.TICKER] = ticker
            tick[Datacode.TIMESTAMP] = time.time()

            if 'regularMarketPrice' not in price:
                return None

            tick[Datacode.PREV_CLOSE] = self.save_wrapper(lambda: float(price['regularMarketPreviousClose']['raw']))
            tick[Datacode.OPEN] = self.save_wrapper(lambda: float(price['regularMarketOpen']['raw']))
            tick[Datacode.CHANGE] = self.save_wrapper(lambda: float(price['regularMarketChange']['raw']))
            tick[Datacode.CHANGE_IN_PERCENT] = self.save_wrapper(lambda: float(price['regularMarketChangePercent']['raw']))

            tick[Datacode.LOW] = self.save_wrapper(lambda: float(price['regularMarketDayLow']['raw']))
            tick[Datacode.HIGH] = self.save_wrapper(lambda: float(price['regularMarketDayHigh']['raw']))

            tick[Datacode.LAST_PRICE] = self.save_wrapper(lambda: float(price['regularMarketPrice']['raw']))
            tick[Datacode.VOLUME] = self.save_wrapper(lambda: float(price['regularMarketVolume']['raw']))
            tick[Datacode.AVG_DAILY_VOL_3MONTH] = self.save_wrapper(lambda: float(price['averageDailyVolume3Month']['raw']))
            tick[Datacode.BETA] = self.save_wrapper(lambda: float(defaultKeyStatistics['beta']['raw']))
            tick[Datacode.EPS] = self.save_wrapper(lambda: float(defaultKeyStatistics['trailingEps']['raw']))
            tick[Datacode.PE_RATIO] = self.save_wrapper(lambda: float(summaryDetail['trailingPE']['raw']))

            tick[Datacode.EX_DIV_DATE] = self.save_wrapper(
                lambda: dateutil.parser.parse(summaryDetail['exDividendDate']['fmt'], yearfirst=True, dayfirst=False).date())

            tick[Datacode.LOW_52_WEEK] = self.save_wrapper(lambda: float(summaryDetail['fiftyTwoWeekLow']['raw']))
            tick[Datacode.HIGH_52_WEEK] = self.save_wrapper(lambda: float(summaryDetail['fiftyTwoWeekHigh']['raw']))

            tick[Datacode.MARKET_CAP] = self.save_wrapper(lambda: float(price['marketCap']['raw']))

            tick[Datacode.BID] = self.save_wrapper(lambda: float(summaryDetail['bid']['raw']))
            tick[Datacode.BIDSIZE] = self.save_wrapper(lambda: float(summaryDetail['bidSize']['raw']))

            tick[Datacode.ASK] = self.save_wrapper(lambda: float(summaryDetail['ask']['raw']))
            tick[Datacode.ASKSIZE] = self.save_wrapper(lambda: float(summaryDetail['askSize']['raw']))

            if quoteType:
                t = int(price['regularMarketTime'])
                tz = pytz.timezone(quoteType['timeZoneFullName'])

                tick[Datacode.TIMEZONE] = tz
                dt = datetime.datetime.fromtimestamp(t, tz)

                tick[Datacode.LAST_PRICE_DATE] = dt.date()
                tick[Datacode.LAST_PRICE_TIME] = dt.time()

            tick[Datacode.EXCHANGE] = self.save_wrapper(lambda: price['exchangeName'])
            tick[Datacode.CURRENCY] = self.save_wrapper(lambda: price['currency'])

            tick[Datacode.DIV] = self.save_wrapper(lambda: float(summaryDetail['dividendRate']['raw']))
            tick[Datacode.DIV_YIELD] = self.save_wrapper(lambda: float(summaryDetail['dividendYield']['raw']))

            # fallback to last dividend on mutual funds and ETFs
            if not tick[Datacode.DIV]:
                tick[Datacode.DIV] = self.save_wrapper(lambda: float(defaultKeyStatistics['lastDividendValue']['raw']))

            if default(price, 'quoteType') == 'FUTURE':
                tick[Datacode.TICKER] = self.save_wrapper(lambda: price['underlyingSymbol'])
                tick[Datacode.NAME] = self.save_wrapper(lambda: price['shortName'])
                tick[Datacode.SETTLEMENT_DATE] = self.save_wrapper(
                    lambda: dateutil.parser.parse(summaryDetail['expireDate']['fmt'], yearfirst=True, dayfirst=False).date())
            else:
                tick[Datacode.NAME] = self.save_wrapper(lambda: price['longName'])
                tick[Datacode.EXPIRY_DATE] = self.save_wrapper(
                    lambda: dateutil.parser.parse(summaryDetail['expireDate']['fmt'], yearfirst=True, dayfirst=False).date())
                tick[Datacode.SETTLEMENT_DATE] = None

            if not tick[Datacode.NAME]:
                tick[Datacode.NAME] = tick[Datacode.TICKER]

            tick[Datacode.SECTOR] = self.save_wrapper(lambda: summaryProfile['sector'])
            tick[Datacode.INDUSTRY] = self.save_wrapper(lambda: summaryProfile['industry'])

            tick[Datacode.SHARES_OUT] = self.save_wrapper(lambda: float(defaultKeyStatistics['sharesOutstanding']['raw']))
            tick[Datacode.FREE_FLOAT] = self.save_wrapper(lambda: float(defaultKeyStatistics['floatShares']['raw']))
            tick[Datacode.PAYOUT_RATIO] = self.save_wrapper(lambda: float(summaryDetail['payoutRatio']['raw']))

        except BaseException as e:
            logger.exception("BaseException ticker=%s datacode=%s", ticker, datacode)
            del self.realtime[ticker]
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
            self._read_ticker_json_file(ticker)

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

        # Do not hammer Yahoo if network fetch failed recently for this ticker (60s backoff)
        if ticker in self.fetch_failures and (time.time() - self.fetch_failures[ticker]) < 60:
            if ticker in self.historicdata:
                ticks = self.historicdata[ticker]
                if date in ticks:
                    return self._return_value(ticks[date], datacode)
                if min(ticks) <= date <= max(ticks):
                    return 'Not a trading day \'{}\''.format(date)
            return 'Yahoo rate-limited, retry later'

        if not self.crumb:
            new_crumb = self.fetch_crumb()
            if new_crumb:
                self.crumb = new_crumb

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

            quoted_ticker = urllib.parse.quote(ticker, safe='')
            if self.crumb:
                url = 'https://query1.finance.yahoo.com/v8/finance/chart/{}' \
                      '?period1={}&period2={}&interval=1d&events=history&crumb={}' \
                    .format(quoted_ticker, t1, t2, urllib.parse.quote_plus(self.crumb))
            else:
                # query2 chart endpoint does not require a crumb
                url = 'https://query2.finance.yahoo.com/v8/finance/chart/{}' \
                      '?period1={}&period2={}&interval=1d&events=history' \
                    .format(quoted_ticker, t1, t2)

            text = self.urlopen(url)

            with open(os.path.join(self.basedir, 'yahoo-hist-{}.json'.format(ticker)), "w", encoding="utf-8") as csv_file:
                print(text, file=csv_file)

            self._read_ticker_json_file(ticker)

        except HttpException:
            logger.exception("HttpException ticker=%s datacode=%s date=%s", ticker, datacode, date)
            self.fetch_failures[ticker] = time.time()
            return None

        except BaseException as e:
            logger.exception("BaseException ticker=%s datacode=%s date=%s", ticker, datacode, date)
            self.fetch_failures[ticker] = time.time()
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

    def getLatestValue(self, ticker: str, datacode: int, year: int, month: int):
        """
        Retrieve the latest available trading quote for a given year and month.

        :param ticker: the ticker symbol e.g. VOD.L
        :param datacode: the requested datacode
        :param year: year (e.g. 2025)
        :param month: month (1-12)
        :return: requested datacode value on the last trading day of that month
        """
        # remove white space
        ticker = "".join(ticker.split())

        # Determine the last calendar day of the given month
        if month == 12:
            last_date_of_month = datetime.date(year, 12, 31)
        else:
            last_date_of_month = datetime.date(year, month + 1, 1) - datetime.timedelta(days=1)

        # Do not allow querying months completely in the future
        today = datetime.date.today()
        first_date_of_month = datetime.date(year, month, 1)
        if first_date_of_month > today:
            return 'Future date \'{:04d}-{:02d}\''.format(year, month)

        # Target date is either the end of the month or today (if month is current)
        target_date = min(last_date_of_month, today).isoformat()

        # Ensure historical data up to target_date is loaded into self.historicdata
        # We invoke getHistoric for target_date. Even if target_date is a non-trading day,
        # getHistoric will ensure the ticker history is downloaded/cached if needed.
        res = self.getHistoric(ticker, datacode, target_date)

        # Propagate fetch failures immediately before checking cached data
        if isinstance(res, str) and not res.startswith("Not a trading day"):
            return res
        if res is None:
            return 'No data available for ticker \'{}\''.format(ticker)

        if ticker in self.historicdata:
            ticks = self.historicdata[ticker]
            month_prefix = '{:04d}-{:02d}'.format(year, month)
            # Find all trading days in ticks for this year and month that are <= target_date
            month_ticks = [d for d in ticks if d.startswith(month_prefix) and d <= target_date]
            if month_ticks:
                latest_trading_day = max(month_ticks)
                return self._return_value(ticks[latest_trading_day], datacode)

            if target_date < min(ticks):
                return 'Date before available history \'{:04d}-{:02d}\''.format(year, month)

            return 'No trading day in \'{:04d}-{:02d}\''.format(year, month)

        return 'No data available for ticker \'{}\''.format(ticker)


def createInstance(ctx):
    return Yahoo(ctx)
