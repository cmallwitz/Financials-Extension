#  baseclient.py
#
#  license: GNU LGPL
#
#  This library is free software; you can redistribute it and/or
#  modify it under the terms of the GNU Lesser General Public
#  License as published by the Free Software Foundation; either
#  version 3 of the License, or (at your option) any later version.


import codecs
import gzip
import logging
import os
import pathlib
import random
import select
import urllib.request
import urllib.parse
from http import cookiejar
from http.client import HTTPConnection, HTTPSConnection, HTTPException

from datacode import Datacode

logger = logging.getLogger(__name__)


# logger.setLevel(logging.DEBUG)


class RedirectException(HTTPException):
    def __init__(self, location):
        self.location = location


class HttpException(HTTPException):
    def __init__(self, url, response):
        self.url = url
        self.response = response

    def __str__(self):
        if self.response is None:
            return f"url='{self.url}'"
        if type(self.response) is str:
            return f"url='{self.url}' status='{self.response}'"
        if self.response.headers:
            h = '\n'.join(sorted(self.response.headers.__str__().splitlines(), key=lambda l: l.lower()))
            return f"url='{self.url}' status={self.response.status} reason='{self.response.reason}'{h}\n"
        else:
            return f"url='{self.url}' status={self.response.status} reason='{self.response.reason}'"


class BaseClient:
    def __init__(self):
        self.connections = {}
        self.cookies = cookiejar.CookieJar()
        self.last_url = None
        self.redirect_count = 0  # will be set later

        self.basedir = os.path.join(str(pathlib.Path.home()), '.financials-extension')
        os.makedirs(self.basedir, exist_ok=True)

        user_agents = [
            'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0',
            'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:129.0) Gecko/20100101 Firefox/129.0',
            'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:130.0) Gecko/20100101 Firefox/130.0',
            'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:131.0) Gecko/20100101 Firefox/131.0',
            'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:132.0) Gecko/20100101 Firefox/132.0',
            'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:133.0) Gecko/20100101 Firefox/133.0',
        ]

        self.default_headers = {
            'User-Agent': random.sample(user_agents, 1)[0],
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
            'Cache-Control': 'max-age=0'
        }

        self.response = None

    def request(self, method: str, url: str, data=None, headers={}, **kwargs):

        _headers = self.default_headers.copy()
        if headers:
            for key, value in headers.items():
                _headers[key] = value

        if method == 'POST' and 'Content-Type' not in _headers:
            _headers['Content-Type'] = 'application/x-www-form-urlencoded'

        connection = None

        scheme, _, host, path = url.split('/', 3)

        if (scheme, host) in self.connections:
            connection = self.connections.get((scheme, host))

        if connection and select.select([connection.sock], [], [], 0)[0]:
            connection.close()
            connection = None

        if not connection:
            logger.debug('Creating connection --------------------------------------------------')
            connection = HTTPConnection(host, **kwargs) if scheme == 'http:' else HTTPSConnection(host, **kwargs)

        logger.debug('Creating request -----------------------------------------------------')
        logger.debug("%s %s", method, url)

        self.last_url = url

        # generate and add cookie headers
        request = urllib.request.Request(url)

        self.cookies.add_cookie_header(request)
        if request.get_header('Cookie'):
            _headers['Cookie'] = request.get_header('Cookie')

        for key, value in _headers.items():
            logger.debug('Header: %s=%s', key, value)

        # request
        connection.request(method, '/' + path, data, _headers)
        response = connection.getresponse()

        logger.debug('Processing response --------------------------------------------------')

        logger.debug('response.status=%s', response.status)
        for key, value in response.getheaders():
            logger.debug('Header: %s=%s', key, value)

        self.cookies.extract_cookies(response, request)
        self.connections[(scheme, host)] = connection

        return response

    def urlopen(self, url, redirect=True, data=None, headers={}, cookies=[], **kwargs):

        if cookies:
            for c in cookies:
                self.cookies.set_cookie(c)

        self.last_url = None

        self.response = self.request('POST' if data else 'GET', url, data, headers, **kwargs)
        text = self.response.read()

        # Allow redirects - used by Yahoo for some cookie based consent
        self.redirect_count = 5

        # (for Yahoo) AWS CloudFront occasionally returns an incorrect, cached error responses
        # try mitigating by re-requesting straight away
        if 400 <= self.response.status < 500:
            if self.response.getheader('X-Cache') == 'Error from cloudfront':
                self.response = self.request('POST' if data else 'GET', url, data, headers, **kwargs)
                text = self.response.read()

        while 300 <= self.response.status < 400 and self.redirect_count >= 0:

            self.redirect_count -= 1
            location = str(self.response.getheader('Location'))
            location = location.replace(' ', '%20')  # FT bug workaround - this should not be necessary

            if location and redirect:

                if location.startswith('/'):
                    scheme, _, host, path = url.split('/', 3)
                    location = '{}//{}{}'.format(scheme, host, location)

                self.response = self.request('GET', location, None, headers, **kwargs)
                text = self.response.read()

            else:
                raise RedirectException(location)

        if self.response.status >= 400:
            logger.warning("last_url='%s' status=%s reason='%s' headers=%s", self.last_url, self.response.status,
                           self.response.reason,
                           '\n'.join(sorted(self.response.headers.__str__().splitlines(), key=lambda l: l.lower())))
            raise HttpException(url, self.response)

        if self.response.getheader('Content-Encoding') == 'gzip':
            text = gzip.decompress(text)

        content_type = self.response.headers.get_content_charset()
        if content_type is None:
            content_type = 'utf-8'
        text = codecs.decode(text, encoding=content_type, errors='ignore')

        return text

    def get_ticker(self):

        tick = {}

        tick[Datacode.ADJ_CLOSE] = None
        tick[Datacode.ASKSIZE] = None
        tick[Datacode.ASK] = None
        tick[Datacode.AVG_DAILY_VOL_3MONTH] = None
        tick[Datacode.BETA] = None
        tick[Datacode.BIDSIZE] = None
        tick[Datacode.BID] = None
        tick[Datacode.CHANGE] = None
        tick[Datacode.CHANGE_IN_PERCENT] = None
        tick[Datacode.CURRENCY] = None
        tick[Datacode.DIV] = None
        tick[Datacode.DIV_YIELD] = None
        tick[Datacode.EPS] = None
        tick[Datacode.EXCHANGE] = None
        tick[Datacode.EXPIRY_DATE] = None
        tick[Datacode.EX_DIV_DATE] = None
        tick[Datacode.FREE_FLOAT] = None
        tick[Datacode.SETTLEMENT_DATE] = None
        tick[Datacode.HIGH] = None
        tick[Datacode.HIGH_52_WEEK] = None
        tick[Datacode.INDUSTRY] = None
        tick[Datacode.LAST_PRICE] = None
        tick[Datacode.LAST_PRICE_DATE] = None
        tick[Datacode.LAST_PRICE_TIME] = None
        tick[Datacode.LOW] = None
        tick[Datacode.LOW_52_WEEK] = None
        tick[Datacode.MARKET_CAP] = None
        tick[Datacode.NAME] = None
        tick[Datacode.OPEN] = None
        tick[Datacode.PAYOUT_RATIO] = None
        tick[Datacode.PE_RATIO] = None
        tick[Datacode.PREV_CLOSE] = None
        tick[Datacode.SECTOR] = None
        tick[Datacode.SHARES_OUT] = None
        tick[Datacode.TICKER] = None
        tick[Datacode.TIMEZONE] = None
        tick[Datacode.VOLUME] = None

        tick[Datacode.TIMESTAMP] = None

        return tick

    def _return_value(self, data: dict, datacode: int):

        """
        Format data from tick data to out put format - mostly formatting date/time

        :param data: tick data
        :param datacode: the requested datacode
        :return: value or None
        """

        if data is None:
            return None

        try:
            if datacode == Datacode.PREV_CLOSE.value and Datacode.PREV_CLOSE in data:
                return data[Datacode.PREV_CLOSE]

            elif datacode == Datacode.OPEN.value and Datacode.OPEN in data:
                return data[Datacode.OPEN]

            elif datacode == Datacode.CHANGE.value and Datacode.CHANGE in data:
                return data[Datacode.CHANGE]

            elif datacode == Datacode.LAST_PRICE_DATE.value and Datacode.LAST_PRICE_DATE in data:
                if data[Datacode.LAST_PRICE_DATE]:
                    return data[Datacode.LAST_PRICE_DATE].isoformat()
                else:
                    return data[Datacode.LAST_PRICE_DATE]

            elif datacode == Datacode.LAST_PRICE_TIME.value and Datacode.LAST_PRICE_TIME in data:
                if data[Datacode.LAST_PRICE_TIME]:
                    return data[Datacode.LAST_PRICE_TIME].isoformat()
                else:
                    return data[Datacode.LAST_PRICE_TIME]

            elif datacode == Datacode.CHANGE_IN_PERCENT.value and Datacode.CHANGE_IN_PERCENT in data:
                return data[Datacode.CHANGE_IN_PERCENT]

            elif datacode == Datacode.LOW.value and Datacode.LOW in data:
                return data[Datacode.LOW]

            elif datacode == Datacode.HIGH.value and Datacode.HIGH in data:
                return data[Datacode.HIGH]

            elif datacode == Datacode.LAST_PRICE.value and Datacode.LAST_PRICE in data:
                return data[Datacode.LAST_PRICE]

            elif datacode == Datacode.BID.value and Datacode.BID in data:
                return data[Datacode.BID]

            elif datacode == Datacode.ASK.value and Datacode.ASK in data:
                return data[Datacode.ASK]

            elif datacode == Datacode.BIDSIZE.value and Datacode.BIDSIZE in data:
                return data[Datacode.BIDSIZE]

            elif datacode == Datacode.ASKSIZE.value and Datacode.ASKSIZE in data:
                return data[Datacode.ASKSIZE]

            elif datacode == Datacode.LOW_52_WEEK.value and Datacode.LOW_52_WEEK in data:
                return data[Datacode.LOW_52_WEEK]

            elif datacode == Datacode.HIGH_52_WEEK.value and Datacode.HIGH_52_WEEK in data:
                return data[Datacode.HIGH_52_WEEK]

            elif datacode == Datacode.MARKET_CAP.value and Datacode.MARKET_CAP in data:
                return data[Datacode.MARKET_CAP]

            elif datacode == Datacode.VOLUME.value and Datacode.VOLUME in data:
                return data[Datacode.VOLUME]

            elif datacode == Datacode.AVG_DAILY_VOL_3MONTH.value and Datacode.AVG_DAILY_VOL_3MONTH in data:
                return data[Datacode.AVG_DAILY_VOL_3MONTH]

            elif datacode == Datacode.BETA.value and Datacode.BETA in data:
                return data[Datacode.BETA]

            elif datacode == Datacode.EPS.value and Datacode.EPS in data:
                return data[Datacode.EPS]

            elif datacode == Datacode.PE_RATIO.value and Datacode.PE_RATIO in data:
                return data[Datacode.PE_RATIO]

            elif datacode == Datacode.DIV.value and Datacode.DIV in data:
                return data[Datacode.DIV]

            elif datacode == Datacode.DIV_YIELD.value and Datacode.DIV_YIELD in data:
                return data[Datacode.DIV_YIELD]

            elif datacode == Datacode.EX_DIV_DATE.value and Datacode.EX_DIV_DATE in data:
                if data[Datacode.EX_DIV_DATE]:
                    return data[Datacode.EX_DIV_DATE].isoformat()
                else:
                    return data[Datacode.EX_DIV_DATE]

            elif datacode == Datacode.PAYOUT_RATIO.value and Datacode.PAYOUT_RATIO in data:
                return data[Datacode.PAYOUT_RATIO]

            elif datacode == Datacode.EXPIRY_DATE.value and Datacode.EXPIRY_DATE in data:
                if data[Datacode.EXPIRY_DATE]:
                    return data[Datacode.EXPIRY_DATE].isoformat()
                else:
                    return data[Datacode.EXPIRY_DATE]

            elif datacode == Datacode.FREE_FLOAT.value and Datacode.FREE_FLOAT in data:
                return data[Datacode.FREE_FLOAT]

            elif datacode == Datacode.SETTLEMENT_DATE.value and Datacode.SETTLEMENT_DATE in data:
                if data[Datacode.SETTLEMENT_DATE]:
                    return data[Datacode.SETTLEMENT_DATE].isoformat()
                else:
                    return data[Datacode.SETTLEMENT_DATE]

            elif datacode == Datacode.SHARES_OUT.value and Datacode.SHARES_OUT in data:
                return data[Datacode.SHARES_OUT]

            elif datacode == Datacode.CLOSE.value and Datacode.CLOSE in data:
                return data[Datacode.CLOSE]

            elif datacode == Datacode.ADJ_CLOSE.value and Datacode.ADJ_CLOSE in data:
                return data[Datacode.ADJ_CLOSE]

            elif datacode == Datacode.SECTOR.value and Datacode.SECTOR in data:
                return data[Datacode.SECTOR]

            elif datacode == Datacode.INDUSTRY.value and Datacode.INDUSTRY in data:
                return data[Datacode.INDUSTRY]

            elif datacode == Datacode.TICKER.value and Datacode.TICKER in data:
                return data[Datacode.TICKER]

            elif datacode == Datacode.EXCHANGE.value and Datacode.EXCHANGE in data:
                return data[Datacode.EXCHANGE]

            elif datacode == Datacode.CURRENCY.value and Datacode.CURRENCY in data:
                return data[Datacode.CURRENCY]

            elif datacode == Datacode.NAME.value and Datacode.NAME in data:
                return data[Datacode.NAME]

            elif datacode == Datacode.TIMEZONE.value and Datacode.TIMEZONE in data:
                if data[Datacode.TIMEZONE] is not None and type(data[Datacode.TIMEZONE]) != str:
                    return str(data[Datacode.TIMEZONE])
                else:
                    return data[Datacode.TIMEZONE]

        except BaseException as e:
            return 'BaseClient.return_value(\'{}\', {}) - {}'.format(data, datacode, e)

        return "Data doesn't exist - {}".format(datacode)

    def save_wrapper(self, f):
        try:
            value = f()
            logger.debug(value)
            return value
        except BaseException as e:
            pass

        return None

    def close(self):
        for connection in self.connections.values():
            try:
                connection.close()
            except BaseException:
                pass
        self.connections = {}
