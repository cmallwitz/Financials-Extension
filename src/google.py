#  google.py
#
#  license: GNU LGPL
#
#  This library is free software; you can redistribute it and/or
#  modify it under the terms of the GNU Lesser General Public
#  License as published by the Free Software Foundation; either
#  version 3 of the License, or (at your option) any later version.


import datetime
import locale
import logging
import html
import re
import time
import traceback

import urllib.parse

from datacode import Datacode
from baseclient import BaseClient

logger = logging.getLogger(__name__)
# logger.setLevel(logging.DEBUG)


def handle_abbreviations(s):
    s = str(s).strip()
    if s.endswith('T'):
        return float(s.replace('T', ''))*1000
    if s.endswith('M'):
        return float(s.replace('M', ''))*1000000
    if s.endswith('B'):
        return float(s.replace('B', ''))*1000000000
    return float(s)


class Google(BaseClient):
    def __init__(self, ctx):
        super().__init__()

        self.realtime = {}

    def getRealtime(self, ticker: str, datacode: int):

        """
        Retrieve realtime data for ticker from Google Finance and cache it for further lookups

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

        url = 'https://finance.google.com/finance?{}'.format(urllib.parse.urlencode({'q': ticker}))

        try:
            text = self.urlopen(url)
        except BaseException as e:
            logger.error(traceback.format_exc())
            return 'Google.getRealtime(\'{}\', {}) - read: {}'.format(ticker, datacode, e)

        try:
            r = '<meta\s*itemprop="([^"]+)"\s*content="([^"]+)"\s*/>'
            pattern = re.compile(r)
            result = pattern.findall(text)

            if len(result) == 0:
                return None

            if ticker not in self.realtime:
                self.realtime[ticker] = {}

            tick = self.realtime[ticker]

            for key, value in result:

                if key == 'exchangeTimezone':
                    tick[Datacode.TIMEZONE] = self.save_wrapper(lambda: str(value))

                elif key == 'priceChange':
                    tick[Datacode.CHANGE] = self.save_wrapper(lambda: float(value))

                elif key == 'quoteTime':
                    try:
                        dt = datetime.datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")
                        tick[Datacode.LAST_PRICE_DATE] = dt.date()
                        tick[Datacode.LAST_PRICE_TIME] = dt.time()
                    except:
                        pass

                elif key == 'priceChangePercent':
                    tick[Datacode.CHANGE_IN_PERCENT] = self.save_wrapper(lambda: (float(value)))

                elif key == 'price':
                    locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
                    tick[Datacode.LAST_PRICE] = self.save_wrapper(lambda: locale.atof(str(value)))

                elif key == 'priceCurrency':
                    tick[Datacode.CURRENCY] = self.save_wrapper(lambda: str(value))

                elif key == 'exchange':
                    tick[Datacode.EXCHANGE] = self.save_wrapper(lambda: str(value))

                elif key == 'name':
                    tick[Datacode.NAME] = self.save_wrapper(lambda: html.unescape(str(value)))

                elif key == 'tickerSymbol':
                    tick[Datacode.TICKER] = self.save_wrapper(lambda: str(value))

                else:
                    logger.info('ignored key=%s value=%s', key, value)

            start = 0

            r = '<td[^>]+data-snapfield="range">[^<]+</td>\s*<td class="val">\s*([^<]+)\s*</td>'
            pattern = re.compile(r, flags=re.DOTALL)
            match = pattern.search(text, start)

            if match:
                lowhigh = self.save_wrapper(
                    lambda: list(map(
                        lambda s: float(s),
                        html.unescape(match.group(1))
                            .replace('-', '').replace(',', '').strip().split())))

                if lowhigh and len(lowhigh) == 2:
                    tick[Datacode.LOW] = lowhigh[0]
                    tick[Datacode.HIGH] = lowhigh[1]
                    start = match.span(0)[1]

            r = '<td[^>]+data-snapfield="range_52week">[^<]+</td>\s*<td class="val">\s*([^<]+)\s*</td>'
            pattern = re.compile(r, flags=re.DOTALL)
            match = pattern.search(text, start)

            if match:
                lowhigh = self.save_wrapper(
                    lambda: list(map(
                        lambda s: float(s),
                        html.unescape(match.group(1))
                            .replace('-', '').replace(',', '').strip().split())))

                if lowhigh and len(lowhigh) == 2:
                    tick[Datacode.LOW_52_WEEK] = lowhigh[0]
                    tick[Datacode.HIGH_52_WEEK] = lowhigh[1]
                    start = match.span(0)[1]

            r = '<td[^>]+data-snapfield="open">[^<]+</td>\s*<td class="val">\s*([^<]+)\s*</td>'
            pattern = re.compile(r, flags=re.DOTALL)
            match = pattern.search(text, start)

            if match:
                tick[Datacode.OPEN] = self.save_wrapper(
                    lambda: float(html.unescape(match.group(1)).replace(',', '').strip()))
                start = match.span(0)[1]

            r = '<td[^>]+data-snapfield="vol_and_avg">[^<]+</td>\s*<td class="val">\s*([^<]+)\s*</td>'
            pattern = re.compile(r, flags=re.DOTALL)
            match = pattern.search(text, start)

            if match:
                volavg = self.save_wrapper(
                    lambda: list(map(
                        lambda s: handle_abbreviations(s),
                        html.unescape(match.group(1)).replace('/', ' ').strip().split())))

                if volavg:
                    if len(volavg) > 0:
                        tick[Datacode.VOLUME] = volavg[0]
                    start = match.span(0)[1]

            r = '<td[^>]+data-snapfield="market_cap">[^<]+</td>\s*<td class="val">\s*([^<]+)'
            pattern = re.compile(r, flags=re.DOTALL)
            match = pattern.search(text, start)

            if match:
                mcap = self.save_wrapper(
                    lambda: handle_abbreviations(html.unescape(match.group(1)).replace('-', ' ').strip()))

                if mcap:
                    tick[Datacode.MARKET_CAP] = mcap

                # start = match.span(0)[1]

            tick[Datacode.TIMESTAMP] = time.time()

            if tick[Datacode.EXCHANGE] == 'CURRENCY' and Datacode.CURRENCY not in tick:
                tick[Datacode.CURRENCY] = ''

            logger.info(tick)

        except BaseException as e:
            logger.warning(traceback.format_exc())
            return 'Google.getRealtime({}, {}) - process: {}'.format(ticker, datacode, e)

        return self._return_value(self.realtime[ticker], datacode)

    def getHistoric(self, ticker, datacode, date):
        return 'Google.getHistoric: Historic Data not implemented.'


def createInstance(ctx):
    return Google(ctx)
