#  financials_ft.py
#
#  license: GNU LGPL
#
#  This library is free software; you can redistribute it and/or
#  modify it under the terms of the GNU Lesser General Public
#  License as published by the Free Software Foundation; either
#  version 3 of the License, or (at your option) any later version.

import html
import logging
import os
import re
import time

import dateutil.parser

import jsonParser
from baseclient import BaseClient
from datacode import Datacode
from tz import whois_timezone_info

logger = logging.getLogger(__name__)


# logger.setLevel(logging.DEBUG)


def handle_abbreviations(s):
    s = str(s).strip().replace(',', '')
    if s.endswith('k'):
        return float(s[:-1]) * 1000
    elif s.endswith('m'):
        return float(s[:-1]) * 1000000
    elif s.endswith('bn'):
        return float(s[:-2]) * 1000000000
    elif s.endswith('tn'):
        return float(s[:-2]) * 1000000000000
    return float(s)


class FT(BaseClient):

    def __init__(self, ctx):
        super().__init__()

        self.crumb = None
        self.realtime = {}
        self.historicdata = {}
        self.js = jsonParser.jsonObject

    def getRealtime(self, ticker: str, datacode: int):

        """
        Retrieve data for ticker from Alpha Vantage and cache it for further lookups

        :param ticker: the ticker symbol e.g. VOD.LON
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
            self.realtime[ticker] = {}

        tick = self.realtime[ticker]

        asset_class = self.guess_asset_class(ticker)

        url = f'https://markets.ft.com/data/{asset_class}/tearsheet/summary?s={ticker}'

        try:
            text = self.urlopen(url, redirect=True, data=None, headers=None)
        except BaseException as e:
            logger.exception("BaseException ticker=%s datacode=%s", ticker, datacode)
            return f'FT.getRealtime({ticker}, {datacode}) - urlopen endpoint: {str(e)}'

        try:
            with open(os.path.join(self.basedir, f'ft-{ticker}.html'), "w", encoding="utf-8") as text_file:
                print(f"<!-- '{self.last_url}' -->\r\n\r\n{text}", file=text_file)
        except BaseException as e:
            logger.exception("BaseException ticker=%s datacode=%s", ticker, datacode)

        tick[Datacode.TIMESTAMP] = time.time()

        tick[Datacode.NAME] = None
        tick[Datacode.TICKER] = None
        tick[Datacode.CURRENCY] = None
        tick[Datacode.LAST_PRICE] = None
        tick[Datacode.CHANGE] = None
        tick[Datacode.CHANGE_IN_PERCENT] = None
        tick[Datacode.VOLUME] = None
        tick[Datacode.LOW_52_WEEK] = None
        tick[Datacode.HIGH_52_WEEK] = None
        tick[Datacode.LAST_PRICE_DATE] = None
        tick[Datacode.LAST_PRICE_TIME] = None
        tick[Datacode.TIMEZONE] = None

        tick[Datacode.OPEN] = None
        tick[Datacode.HIGH] = None
        tick[Datacode.LOW] = None
        tick[Datacode.PREV_CLOSE] = None
        tick[Datacode.MARKET_CAP] = None

        tick[Datacode.EXCHANGE] = None
        tick[Datacode.AVG_DAILY_VOL_3MONTH] = None
        tick[Datacode.BETA] = None
        tick[Datacode.EPS] = None
        tick[Datacode.PE_RATIO] = None
        tick[Datacode.DIV] = None
        tick[Datacode.DIV_YIELD] = None
        tick[Datacode.EX_DIV_DATE] = None
        tick[Datacode.PAYOUT_RATIO] = None

        try:
            r = '<h1 class="mod-tearsheet-overview__header__name mod-tearsheet-overview__header__name--large">(.*?)</h1>'
            match = re.compile(r, flags=re.DOTALL).search(text)
            if not match:
                return None
            start = match.span(0)[1]

            tick[Datacode.NAME] = self.save_wrapper(
                lambda: html.unescape(match.group(1)).strip())

            r = '<div class="mod-tearsheet-overview__header__symbol">(?:<div [^>]*>)?<span *[^>]*>(.*?)<'
            match = re.compile(r, flags=re.DOTALL).search(text, start)
            if match:
                start = match.span(0)[1]
                tick[Datacode.TICKER] = self.save_wrapper(
                    lambda: html.unescape(match.group(1)).strip())

            r = '<div class="mod-tearsheet-overview__esi">(.*?)<i.*?</i>(.*?)<'
            match = re.compile(r, flags=re.DOTALL).search(text, start)
            if match:
                start = match.span(0)[1]
                tick[Datacode.SECTOR] = self.save_wrapper(
                    lambda: html.unescape(match.group(1)).strip())
                tick[Datacode.INDUSTRY] = self.save_wrapper(
                    lambda: html.unescape(match.group(2)).strip())

            r = r'<span [^>]*>Price \(([A-Z]+|--)\)</span><span [^>]*>([0-9,\.]+)</span>'
            match = re.compile(r, flags=re.DOTALL).search(text, start)
            if match:
                start = match.span(0)[1]
                if match.group(1) != '--':
                    tick[Datacode.CURRENCY] = self.save_wrapper(
                        lambda: html.unescape(match.group(1)).strip())
                tick[Datacode.LAST_PRICE] = self.save_wrapper(
                    lambda: float(html.unescape(match.group(2)).replace(',', '').strip()))

            r = r'<span[^>]*>Today\'s Change</span><span[^>]*><span[^>]*>(?:<i[^>]*></i>)?([0-9,\.-]+) */ *([0-9,\.-]+)%</span>'
            match = re.compile(r, flags=re.DOTALL).search(text, start)
            if match:
                start = match.span(0)[1]
                tick[Datacode.CHANGE] = self.save_wrapper(
                    lambda: float(html.unescape(match.group(1)).replace(',', '').strip()))
                tick[Datacode.CHANGE_IN_PERCENT] = self.save_wrapper(
                    lambda: float(html.unescape(match.group(2)).replace(',', '').strip()))

            r = r'<span[^>]*>Shares traded</span><span[^>]*>([0-9mk,\.]+)</span>'
            match = re.compile(r, flags=re.DOTALL).search(text, start)
            if match:
                start = match.span(0)[1]
                tick[Datacode.VOLUME] = self.save_wrapper(
                    lambda: handle_abbreviations(html.unescape(match.group(1))))

            r = r'<span[^>]*>Beta</span><span[^>]*>([0-9,\.]+)</span>'
            match = re.compile(r, flags=re.DOTALL).search(text, start)
            if match:
                start = match.span(0)[1]
                tick[Datacode.BETA] = self.save_wrapper(
                    lambda: handle_abbreviations(html.unescape(match.group(1))))

            r = r'<span[^>]*>52 week range</span><span[^>]*>([0-9,\.]+) *- *([0-9,\.]+)</span>'
            match = re.compile(r, flags=re.DOTALL).search(text, start)
            if match:
                start = match.span(0)[1]
                tick[Datacode.LOW_52_WEEK] = self.save_wrapper(
                    lambda: float(html.unescape(match.group(1)).replace(',', '').strip()))
                tick[Datacode.HIGH_52_WEEK] = self.save_wrapper(
                    lambda: float(html.unescape(match.group(2)).replace(',', '').strip()))

            r = r'<div class="mod-disclaimer">.+?as of (.+?)\.?</div>'
            match = re.compile(r, flags=re.DOTALL).search(text, start)
            if match:
                start = match.span(0)[1]

                try:
                    value = html.unescape(match.group(1)).strip()
                    dt = dateutil.parser.parse(value, yearfirst=True, dayfirst=False, tzinfos=whois_timezone_info)
                    tick[Datacode.LAST_PRICE_DATE] = dt.date()
                    tick[Datacode.LAST_PRICE_TIME] = dt.time()

                    time_bits = value.split(' ')
                    if len(time_bits) >= 4:
                        tick[Datacode.TIMEZONE] = time_bits[-1]

                except BaseException as e:
                    pass

            # second attempt at 52 week range
            if Datacode.LOW_52_WEEK not in tick or not tick[Datacode.LOW_52_WEEK]:
                r = r'<span class="mod-ui-range-bar__container__label--lo"><span[^>]*>([0-9,\.]+)</span>'
                match = re.compile(r, flags=re.DOTALL).search(text, start)
                if match:
                    tick[Datacode.LOW_52_WEEK] = self.save_wrapper(
                        lambda: float(html.unescape(match.group(1)).replace(',', '').strip()))

            if Datacode.HIGH_52_WEEK not in tick or not tick[Datacode.HIGH_52_WEEK]:
                r = r'<span class="mod-ui-range-bar__container__label--hi"><span[^>]*>([0-9,\.]+)</span>'
                match = re.compile(r, flags=re.DOTALL).search(text, start)
                if match:
                    tick[Datacode.HIGH_52_WEEK] = self.save_wrapper(
                        lambda: float(html.unescape(match.group(1)).replace(',', '').strip()))

            # just moving forward to data table
            r = '<div class="mod-tearsheet-key-stats__data__table">'
            match = re.compile(r, flags=re.DOTALL).search(text, start)
            if match:
                start = match.span(0)[1]

            r = r'<th>Open</th><td>([0-9,\.]+)</td>'
            match = re.compile(r, flags=re.DOTALL).search(text, start)
            if match:
                tick[Datacode.OPEN] = self.save_wrapper(
                    lambda: float(html.unescape(match.group(1)).replace(',', '').strip()))

            r = r'<th>High</th><td>([0-9,\.]+)</td>'
            match = re.compile(r, flags=re.DOTALL).search(text, start)
            if match:
                tick[Datacode.HIGH] = self.save_wrapper(
                    lambda: float(html.unescape(match.group(1)).replace(',', '').strip()))

            r = r'<th>Low</th><td>([0-9,\.]+)</td>'
            match = re.compile(r, flags=re.DOTALL).search(text, start)
            if match:
                tick[Datacode.LOW] = self.save_wrapper(
                    lambda: float(html.unescape(match.group(1)).replace(',', '').strip()))

            r = r'<th>\s*Previous close\s*</th><td>\s*([0-9,\.]+)\s*</td>'
            match = re.compile(r, flags=re.DOTALL).search(text, start)
            if match:
                tick[Datacode.PREV_CLOSE] = self.save_wrapper(
                    lambda: float(html.unescape(match.group(1)).replace(',', '').strip()))

            r = r'<th>\s*Average volume\s*</th><td>\s*([0-9,\.btnm]+)\s*</td>'
            match = re.compile(r, flags=re.DOTALL).search(text, start)
            if match:
                tick[Datacode.AVG_DAILY_VOL_3MONTH] = self.save_wrapper(
                    lambda: handle_abbreviations(html.unescape(match.group(1))))

            r = r'<th>\s*P/E.*?</th><td>\s*([0-9,\.\-]+)\s*<'
            match = re.compile(r, flags=re.DOTALL).search(text, start)
            if match:
                value = html.unescape(match.group(1))
                if value == '--':
                    tick[Datacode.PE_RATIO] = 0.0
                else:
                    tick[Datacode.PE_RATIO] = self.save_wrapper(
                        lambda: float(value))

            r = r'<th>\s*Market cap\s*</th><td>\s*([0-9,\.btnm]+)\s*<'
            match = re.compile(r, flags=re.DOTALL).search(text, start)
            if match:
                tick[Datacode.MARKET_CAP] = self.save_wrapper(
                    lambda: handle_abbreviations(html.unescape(match.group(1))))

            r = r'<th>\s*EPS.*?</th><td>\s*([0-9,\.\-]+)\s*<'
            match = re.compile(r, flags=re.DOTALL).search(text, start)
            if match:
                tick[Datacode.EPS] = self.save_wrapper(
                    lambda: float(html.unescape(match.group(1))))

            r = r'<th>\s*Annual div.*?</th><td>\s*([0-9,\.]+)\s*<'
            match = re.compile(r, flags=re.DOTALL).search(text, start)
            if match:
                tick[Datacode.DIV] = self.save_wrapper(
                    lambda: float(html.unescape(match.group(1))))

            r = r'<th>\s*Annual div yield.*?</th><td>\s*([0-9,\.]+)%\s*<'
            match = re.compile(r, flags=re.DOTALL).search(text, start)
            if match:
                tick[Datacode.DIV_YIELD] = self.save_wrapper(
                    lambda: float(html.unescape(match.group(1))))

            r = r'<th>\s*Div ex-date\s*</th><td><span[^>]*>(.*?)</span><'
            match = re.compile(r, flags=re.DOTALL).search(text, start)
            if match:
                try:
                    value = html.unescape(match.group(1)).strip()
                    dt = dateutil.parser.parse(value, yearfirst=True, dayfirst=False, tzinfos=whois_timezone_info)
                    tick[Datacode.EX_DIV_DATE] = dt.date()
                except BaseException as e:
                    pass

        except BaseException as e:
            logger.exception("BaseException ticker=%s datacode=%s", ticker, datacode)
            return f'FT.getRealtime({ticker}, {datacode}) - process: {str(e)}'

        logger.info(tick)

        return self._return_value(self.realtime[ticker], datacode)

    def getHistoric(self, ticker, datacode, date):
        return 'FT.getHistoric: Historic Data not implemented.'

    def guess_asset_class(self, ticker):

        if len(ticker) == 6:
            if ticker[0:2] in ['USD', 'EUR', 'GBP', 'JPY', 'CHF']:
                return 'currencies'
            if ticker[3:5] in ['USD', 'EUR', 'GBP', 'JPY', 'CHF']:
                return 'currencies'

        colon_count = ticker.count(':')

        if colon_count == 0:
            return 'funds'
        elif colon_count == 3:
            return 'etfs'

        return 'equities'


def createInstance(ctx):
    return FT(ctx)
