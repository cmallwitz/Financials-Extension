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
import random
import sys
import select

from http.client import HTTPConnection, HTTPSConnection
from http import cookiejar

import urllib.parse

from datacode import Datacode

def log(str):
    # print(str, file=sys.stderr)
    pass


class BaseClient:
    def __init__(self):
        self.connections = {}
        self.cookies = cookiejar.CookieJar()

        user_agents = [
            'Mozilla/5.0 (X11; Linux x86_64; rv:57.0) Gecko/20100101 Firefox/57.0',
            'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:56.0) Gecko/20100101 Firefox/56.0',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:55.0) Gecko/20100101 Firefox/55.0'
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.79 Safari/537.36',
            'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36'
        ]

        self.default_headers = {
            'User-Agent': random.sample(user_agents, 1)[0],
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8'
        }

    def request(self, method: str, url: str, data=None, headers={}, **kwargs):

        _headers = self.default_headers.copy()
        for key, value in headers.items():
            _headers[key] = value

        connection = None

        scheme, _, host, path = url.split('/', 3)

        if (scheme, host) in self.connections:
            connection = self.connections.get((scheme, host))

        if connection and select.select([connection.sock], [], [], 0)[0]:
            connection.close()
            connection = None

        if not connection:
            log('Creating HHTP connection --------- ----------------------------------------')
            Connection = HTTPConnection if scheme == 'http:' else HTTPSConnection
            connection = Connection(host, **kwargs)

        log('Creating HTTP request ------------ ----------------------------------------')
        log(url)

        # generate and add cookie headers
        request = urllib.request.Request(url)

        self.cookies.add_cookie_header(request)
        if request.get_header('Cookie'):
            _headers['Cookie'] = request.get_header('Cookie')

        for key, value in _headers.items():
            log('{}: {}'.format(key, value))

        # request
        connection.request(method, '/' + path, data, _headers)
        response = connection.getresponse()

        log('Processing HTTP response --------- ----------------------------------------')

        # log('response.status={}'.format(response.status))
        for key, value in response.getheaders():
            log('{}: {}'.format(key, value))

        self.cookies.extract_cookies(response, request)
        self.connections[(scheme, host)] = connection

        return response

    def urlopen(self, url, data=None, headers={}, **kwargs):

        response = self.request('POST' if data else 'GET', url, data, headers, **kwargs)
        text = response.read()

        if 300 <= response.status < 400:

            scheme, _, host, path = url.split('/', 3)
            redirect_to = response.getheader('Location')
            if host not in redirect_to:
                redirect_to = scheme + '//' + host +  redirect_to

            if response.getheader('Location'):
                response = self.request('POST' if data else 'GET', redirect_to, data, headers, **kwargs)
                text = response.read()

        assert response.status < 400, \
            'HTTP Status={} Reason={} url={}'.format(response.status, response.reason, url)

        if response.getheader('Content-Encoding') == 'gzip':
            text = gzip.decompress(text)

        content_type = response.headers.get_content_charset()
        if content_type is None:
            content_type = 'utf-8'
        text = codecs.decode(text, encoding=content_type, errors='ignore')

        return text

    def _return_value(self, data: dict, datacode: int):

        """
        Format data from tick data to out put format - mostly formatting date/time

        :param data: tick data
        :param datacode: the requested datacode
        :return: value or None
        """

        try:
            if datacode == Datacode.PREV_CLOSE.value and Datacode.PREV_CLOSE in data:
                return data[Datacode.PREV_CLOSE]

            elif datacode == Datacode.OPEN.value and Datacode.OPEN in data:
                return data[Datacode.OPEN]

            elif datacode == Datacode.CHANGE.value and Datacode.CHANGE in data:
                return data[Datacode.CHANGE]

            elif datacode == Datacode.LAST_PRICE_DATE.value and Datacode.LAST_PRICE_DATE in data:
                return data[Datacode.LAST_PRICE_DATE].isoformat()

            elif datacode == Datacode.LAST_PRICE_TIME.value and Datacode.LAST_PRICE_TIME in data:
                return data[Datacode.LAST_PRICE_TIME].isoformat()

            elif datacode == Datacode.CHANGE_IN_PERCENT.value and Datacode.CHANGE_IN_PERCENT in data:
                return data[Datacode.CHANGE_IN_PERCENT]

            elif datacode == Datacode.LOW.value and Datacode.LOW in data:
                return data[Datacode.LOW]

            elif datacode == Datacode.HIGH.value and Datacode.HIGH in data:
                return data[Datacode.HIGH]

            elif datacode == Datacode.LAST_PRICE.value and Datacode.LAST_PRICE in data:
                return data[Datacode.LAST_PRICE]

            elif datacode == Datacode.VOLUME.value and Datacode.VOLUME in data:
                return data[Datacode.VOLUME]

            elif datacode == Datacode.AVG_DAILY_VOL_3MOMTH.value and Datacode.AVG_DAILY_VOL_3MOMTH in data:
                return data[Datacode.AVG_DAILY_VOL_3MOMTH]

            elif datacode == Datacode.CLOSE.value and Datacode.CLOSE in data:
                return data[Datacode.CLOSE]

            elif datacode == Datacode.ADJ_CLOSE.value and Datacode.ADJ_CLOSE in data:
                return data[Datacode.ADJ_CLOSE]

            elif datacode == Datacode.TICKER.value and Datacode.TICKER in data:
                return data[Datacode.TICKER]

            elif datacode == Datacode.EXCHANGE.value and data[Datacode.EXCHANGE]:
                return data[Datacode.EXCHANGE]

            elif datacode == Datacode.CURRENCY.value and data[Datacode.CURRENCY]:
                return data[Datacode.CURRENCY]

            elif datacode == Datacode.NAME.value and data[Datacode.NAME]:
                return data[Datacode.NAME]

            elif datacode == Datacode.TIMEZONE.value and data[Datacode.TIMEZONE]:
                return str(data[Datacode.TIMEZONE])

            return 'Data doesn\'t exist - {}'.format(datacode)

        except BaseException as e:
            return 'BaseClient.return_value(\'{}\', {}) - {}'.format(data, datacode, e)

        return None
