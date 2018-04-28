#  google.py
#
#  license: GNU LGPL
#
#  This library is free software; you can redistribute it and/or
#  modify it under the terms of the GNU Lesser General Public
#  License as published by the Free Software Foundation; either
#  version 3 of the License, or (at your option) any later version.


import dateutil
import locale
import logging
import html
import os
import pathlib
import re
import time
import traceback

import xml.etree.ElementTree as ET
from naivehtmlparser import NaiveHTMLParser

from datacode import Datacode
from baseclient import BaseClient, RedirectException

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
        self.location = None

        self.basedir = os.path.join(str(pathlib.Path.home()), '.financials-extension')
        os.makedirs(self.basedir, exist_ok=True)

    def getRealtime(self, ticker: str, datacode: int):

        """
        Retrieve realtime data for ticker from Google Finance and cache it for further lookups

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

        q_param = 'q=' + ticker

        if not self.location:
            url = 'https://www.google.com/search?hl=en&tbm=fin&' + q_param

            try:
                self.urlopen(url, redirect=False)
            except RedirectException as e:
                self.location = e.location.replace('&' + q_param, '')
            except BaseException as e:
                logger.error(traceback.format_exc())
                return 'Google.getRealtime(\'{}\', {}) - location: {}'.format(ticker, datacode, e)

        if not self.location:
            url = 'https://www.google.com/search?tbm=fin&' + q_param
        else:
            url = self.location + '&' + q_param

        try:
            text = self.urlopen(url)
            with open(os.path.join(self.basedir, 'google-{}.html'.format(ticker)), "w") as text_file:
                print(text, file=text_file)
        except BaseException as e:
            logger.error(traceback.format_exc())
            return 'Google.getRealtime(\'{}\', {}) - urlopen: {} {}'.format(ticker, datacode, e, url)

        if ticker not in self.realtime:
            self.realtime[ticker] = {}

        tick = self.realtime[ticker]

        # after first <div ... role="heading"> - get name
        try:
            r = '<div [^>]+ role="heading">'
            pattern = re.compile(r)
            match = pattern.search(text)

            if not match:
                return 'Google.getRealtime({}, {}) - no match'.format(ticker, datacode)

            start = match.span(0)[1]

            r = '<div [^>]*>(.*?)</div>'
            pattern = re.compile(r)

            # first div ignored
            match = pattern.search(text, start)
            if not match:
                return 'Google.getRealtime({}, {}) - no match'.format(ticker, datacode)
            start = match.span(0)[1]

            # second div is NAME
            match = pattern.search(text, start)
            if not match:
                return 'Google.getRealtime({}, {}) - no match'.format(ticker, datacode)
            start = match.span(0)[1]

            tick[Datacode.NAME] = self.save_wrapper(
                lambda: html.unescape(match.group(1)).strip())

            # third div is TICKER
            match = pattern.search(text, start)
            if not match:
                return 'Google.getRealtime({}, {}) - no match'.format(ticker, datacode)

            ticker = self.save_wrapper(
                lambda: html.unescape(match.group(1)).replace(' ', ''))

            tick[Datacode.EXCHANGE] = self.save_wrapper(lambda: ticker.split(':')[0])
            tick[Datacode.TICKER] = self.save_wrapper(lambda: ticker.split(':')[1])

        except BaseException as e:
            return 'Google.getRealtime({}, {}) - process: {}'.format(ticker, datacode, e)

        try:
            r = '<sticky-header [^>]*>(.*?)</sticky-header>'
            pattern = re.compile(r, flags=re.DOTALL)
            match = re.search(pattern, text)

            if match:
                text = match.group(1)
            else:
                return 'Data for \'{}\' not found'.format(ticker)

            parser = NaiveHTMLParser()
            root = parser.feed(text)
            parser.close()

            cards = root.findall('.//g-card-section')

            if len(cards) < 4:
                return 'Data for \'{}\' not found'.format(ticker)

            header = cards[1]

            locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')

            tick[Datacode.LAST_PRICE] = self.save_wrapper(
                lambda: locale.atof(
                    html.unescape(header.find('./div[1]/span[1]/span[1]/span[1]').text).strip()))

            tick[Datacode.CURRENCY] = self.save_wrapper(
                lambda: html.unescape(header.find('./div[1]/span[1]/span[1]/span[2]').text).strip())

            tick[Datacode.CHANGE] = self.save_wrapper(
                lambda: locale.atof(
                    html.unescape(header.find('./div[1]/span[2]/span[1]').text).replace('−', '-').strip()))

            tick[Datacode.CHANGE_IN_PERCENT] = self.save_wrapper(
                lambda: float(
                    html.unescape(header.find('./div[1]/span[2]/span[2]/span[1]').text).strip()
                        .replace('(', '').replace(')', '').replace('%', '')))

            try:
                value = html.unescape(header.find('./div[2]/span[1]/span[2]').text).replace('·', '').strip()
                logger.debug(value)
                dt = dateutil.parser.parse(value)
                tick[Datacode.LAST_PRICE_DATE] = dt.date()
                tick[Datacode.LAST_PRICE_TIME] = dt.time()

                time_bits = value.split(' ')
                if len(time_bits) >= 4:
                    tick[Datacode.TIMEZONE] = time_bits[-1]

            except BaseException as e:
                pass

            footer = cards[3]
            logger.debug(ET.tostring(footer))

            # parse 'footer' for remaining fields
            table = footer.find('./div[1]/div[1]/div[1]/table[1]')

            tick[Datacode.OPEN] = self.save_wrapper(
                lambda: float(
                    html.unescape(table.find('./tr[1]/td[2]').text).replace(',', '').strip()))

            tick[Datacode.HIGH] = self.save_wrapper(
                lambda: float(
                    html.unescape(table.find('./tr[2]/td[2]').text).replace(',', '').strip()))

            tick[Datacode.LOW] = self.save_wrapper(
                lambda: float(
                    html.unescape(table.find('./tr[3]/td[2]').text).replace(',', '').strip()))

            tick[Datacode.MARKET_CAP] = self.save_wrapper(
                lambda: handle_abbreviations(
                    html.unescape(table.find('./tr[4]/td[2]').text).replace(',', '').replace('-', '').strip()))

            table = footer.find('./div[1]/div[1]/div[2]/table[1]')

            tick[Datacode.PREV_CLOSE] = self.save_wrapper(
                lambda: float(
                    html.unescape(table.find('./tr[2]/td[2]').text).replace(',', '').strip()))

            tick[Datacode.HIGH_52_WEEK] = self.save_wrapper(
                lambda: float(
                    html.unescape(table.find('./tr[3]/td[2]').text).replace(',', '').strip()))

            tick[Datacode.LOW_52_WEEK] = self.save_wrapper(
                lambda: float(
                    html.unescape(table.find('./tr[4]/td[2]').text).replace(',', '').strip()))

            tick[Datacode.TIMESTAMP] = time.time()

            logger.info(tick)

        except BaseException as e:
            logger.warning(traceback.format_exc())
            return 'Google.getRealtime({}, {}) - process: {}'.format(ticker, datacode, e)

        return self._return_value(self.realtime[ticker], datacode)

    def getHistoric(self, ticker, datacode, date):
        return 'Google.getHistoric: Historic Data not implemented.'


def createInstance(ctx):
    return Google(ctx)
