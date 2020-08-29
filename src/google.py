#  google.py
#
#  license: GNU LGPL
#
#  This library is free software; you can redistribute it and/or
#  modify it under the terms of the GNU Lesser General Public
#  License as published by the Free Software Foundation; either
#  version 3 of the License, or (at your option) any later version.


import dateutil
import html
import logging
import os
import re
import time
import traceback
import xml.etree.ElementTree as ET

from baseclient import BaseClient, RedirectException
from datacode import Datacode
from naivehtmlparser import NaiveHTMLParser
from tz import whois_timezone_info

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


def un_span(s):
    return re.sub(r'<span [^>]*>', '', s).replace('</span>', '')


class Google(BaseClient):
    def __init__(self, ctx):
        super().__init__()

        self.realtime = {}
        self.location = None

    def getRealtime(self, ticker: str, datacode: int):

        """
        Retrieve realtime data for ticker from Google Finance and cache it for further lookups

        :param ticker: the ticker symbol e.g. LON:VOD
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
                print(f"<!-- '{url}' -->\r\n\r\n{text}", file=text_file)
        except BaseException as e:
            logger.error(traceback.format_exc())
            return 'Google.getRealtime(\'{}\', {}) - urlopen: {} {}'.format(ticker, datacode, e, url)

        if ticker not in self.realtime:
            self.realtime[ticker] = {}

        tick = self.realtime[ticker]

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
        tick[Datacode.AVG_DAILY_VOL_3MOMTH] = None

        try:
            r = '<span[^>]+role="heading"[^>]+>(.*?)</span>'
            pattern = re.compile(r)

            match = pattern.search(text)
            if not match:
                return None
            start = match.span(0)[1]

            tick[Datacode.NAME] = self.save_wrapper(
                lambda: html.unescape(un_span(match.group(1)).strip()))

            # next div is TICKER
            r = '<div [^>]*><div [^>]*>(.*?)</div></div>'
            pattern = re.compile(r)

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

            tick[Datacode.LAST_PRICE] = self.save_wrapper(
                lambda: float(
                    html.unescape(header.find('./span[1]/span[1]/span[1]').text).replace(',', '').strip()))

            tick[Datacode.CURRENCY] = self.save_wrapper(
                lambda: html.unescape(header.find('./span[1]/span[1]/span[2]').text).strip())

            tick[Datacode.CHANGE] = self.save_wrapper(
                lambda: float(
                    html.unescape(header.find('./span[2]/span[1]').text).replace('−', '-').replace(',', '').strip()))

            # percentage is always wrapped in (...) and always positive even if there is a price drop
            tick[Datacode.CHANGE_IN_PERCENT] = self.save_wrapper(
                lambda: float(
                    html.unescape(header.find('./span[2]/span[2]/span[1]').text).strip()
                        .replace('(', '').replace(')', '').replace('%', '')))

            try:
                value = html.unescape(header.find('./div[1]/span[1]/span[2]').text).replace('·', '').strip()
                logger.debug(value)
                dt = dateutil.parser.parse(value, tzinfos=whois_timezone_info)
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

            # for indices: first item on right side is LOW
            if html.unescape(table.find('./tr[1]/td[1]').text).strip() == 'Low':
                tick[Datacode.LOW] = self.save_wrapper(
                    lambda: float(
                        html.unescape(table.find('./tr[1]/td[2]').text).replace(',', '').strip()))

            tick[Datacode.PREV_CLOSE] = self.save_wrapper(
                lambda: float(
                    html.unescape(table.find('./tr[2]/td[2]').text).replace(',', '').strip()))

            tick[Datacode.HIGH_52_WEEK] = self.save_wrapper(
                lambda: float(
                    html.unescape(table.find('./tr[3]/td[2]').text).replace(',', '').strip()))

            tick[Datacode.LOW_52_WEEK] = self.save_wrapper(
                lambda: float(
                    html.unescape(table.find('./tr[4]/td[2]').text).replace(',', '').strip()))

            logger.info(tick)

        except BaseException as e:
            logger.warning(traceback.format_exc())
            return 'Google.getRealtime({}, {}) - process: {}'.format(ticker, datacode, e)

        return self._return_value(self.realtime[ticker], datacode)

    def getHistoric(self, ticker, datacode, date):
        return 'Google.getHistoric: Historic Data not implemented.'


def createInstance(ctx):
    return Google(ctx)
