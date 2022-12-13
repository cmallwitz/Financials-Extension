#  financials_coinbase.py
#
#  license: GNU LGPL
#
#  This library is free software; you can redistribute it and/or
#  modify it under the terms of the GNU Lesser General Public
#  License as published by the Free Software Foundation; either
#  version 3 of the License, or (at your option) any later version.


import csv
import datetime
import logging
import os
import pprint
import re
import time
import json

import dateutil.parser
import pytz

import jsonParser
from baseclient import BaseClient, HttpException
from datacode import Datacode

logger = logging.getLogger(__name__)


# logger.setLevel(logging.DEBUG)

class Coinbase(BaseClient):
    def __init__(self, ctx):
        super().__init__()

        self.crumb = None
        self.realtime = {}
        self.js = jsonParser.jsonObject

    def getRealtime(self, ticker, datacode):

        """
        Retrieve realtime data for ticker from Coinbase and cache it for further lookups

        :param ticker: the ticker symbol e.g. ETH-EUR
        :param datacode: the requested datacode, not all are supported
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

        url = 'https://api.exchange.coinbase.com/products/{}/stats'.format(ticker)

        try:
            text = self.urlopen(url, redirect=True, data=None, headers=None)
        except BaseException as e:
            logger.exception("BaseException ticker=%s datacode=%s", ticker, datacode)
            return 'Coinbase.getRealtime({}, {}) - urlopen: {}'.format(ticker, datacode, e)

        try:
            with open(os.path.join(self.basedir, 'coinbase-{}.json'.format(ticker)), "w", encoding="utf-8") as text_file:
                print(f"<!-- '{url}' -->\r\n\r\n{text}", file=text_file)
        except BaseException:
            logger.exception("BaseException ticker=%s datacode=%s", ticker, datacode)

        try:
            results = json.loads(text)

        except BaseException as e:
            logger.exception("BaseException ticker=%s datacode=%s", ticker, datacode)
            return 'Coinbase.getRealtime({}, {}) - crumb: {}'.format(ticker, datacode, e)

        try:
            price = results['last']

            if not price:
                return 'Could not find price for \'{}\''.format(ticker)

            if ticker not in self.realtime:
                self.realtime[ticker] =  self.get_ticker()

            tick = self.realtime[ticker]

            tick[Datacode.TIMESTAMP] = time.time()
            tick[Datacode.LAST_PRICE] = float(price)
            tick[Datacode.OPEN] = float(results['open'])
            tick[Datacode.HIGH] = float(results['high'])
            tick[Datacode.LOW] = float(results['low'])
            tick[Datacode.VOLUME] =  float(results['volume'])
            tick[Datacode.TICKER] = ticker.split('-', 1)[0]
            tick[Datacode.CURRENCY] = ticker.split('-', 1)[1]

        except BaseException as e:
            logger.exception("BaseException ticker=%s datacode=%s", ticker, datacode)
            return 'Coinbase.getRealtime({}, {}) - process: {}'.format(ticker, datacode, e)

        return self._return_value(self.realtime[ticker], datacode)

def createInstance(ctx):
    return Coinbase(ctx)
