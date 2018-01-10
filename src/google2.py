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


# TODO migrate to:
# https://www.google.com/search?q=NYSE:IBM&tbm=fin
# https://www.google.com/search?q=NASDAQ:INTC&tbm=fin
# https://www.google.com/search?q=LON:VOD&tbm=fin
# https://www.google.com/search?q=EURGBP
# https://www.google.com/search?q=INDEXSP:.INX


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

        # use cached value for up to 60 seconds
        if ticker in self.realtime:
            tick = self.realtime[ticker]
            if time.time() - 60 < tick[Datacode.TIMESTAMP]:
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
            result = re.findall(pattern, text)

            if len(result) == 0:
                return 'Data for \'{}\' not found'.format(ticker)

            if ticker not in self.realtime:
                self.realtime[ticker] = {}

            tick = self.realtime[ticker]

            for key, value in result:

                if key == 'exchangeTimezone':
                    try:
                        tick[Datacode.TIMEZONE] = str(value)
                    except:
                        pass

                elif key == 'priceChange':
                    try:
                        tick[Datacode.CHANGE] = float(value)
                    except:
                        pass

                elif key == 'quoteTime':
                    try:
                        dt = datetime.datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")
                        tick[Datacode.LAST_PRICE_DATE] = dt.date()
                        tick[Datacode.LAST_PRICE_TIME] = dt.time()
                    except:
                        pass

                elif key == 'priceChangePercent':
                    try:
                        tick[Datacode.CHANGE_IN_PERCENT] = float(value)
                    except:
                        pass

                elif key == 'price':
                    try:
                        locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
                        tick[Datacode.LAST_PRICE] = locale.atof(str(value))
                    except:
                        pass

                elif key == 'priceCurrency':
                    try:
                        tick[Datacode.CURRENCY] = str(value)
                    except:
                        pass

                elif key == 'priceCurrency':
                    pass

                elif key == 'exchange':
                    try:
                        tick[Datacode.EXCHANGE] = str(value)
                    except:
                        pass

                elif key == 'name':
                    try:
                        tick[Datacode.NAME] = html.unescape(str(value))
                    except:
                        pass

                elif key == 'tickerSymbol':
                    try:
                        tick[Datacode.TICKER] = str(value)
                    except:
                        pass

                else:
                    logger.info('ignored key=%s value=%s', key, value)

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
