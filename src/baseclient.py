#  baseclient.py
#
#  license: GNU LGPL
#
#  This library is free software; you can redistribute it and/or
#  modify it under the terms of the GNU Lesser General Public
#  License as published by the Free Software Foundation; either
#  version 3 of the License, or (at your option) any later version.


import logging
import os
import pathlib
import random
from importlib import util
from datacode import Datacode

logger = logging.getLogger(__name__)


# logger.setLevel(logging.DEBUG)


curl_cffi_present = not util.find_spec("curl_cffi") is None
requests_present = not util.find_spec("requests") is None

if curl_cffi_present:
    logger.debug("Importing curl_cffi...")
    from curl_cffi import requests, __version__ as requests_version, __name__ as requests_name
elif requests_present:
    logger.debug("Importing requests...")
    import requests
    requests_version = requests.__version__
    requests_name = requests.__name__
else:
    raise Exception("Neither curl_cffi nor requests found.")

# import requests


class HttpException(Exception):
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
            return f"url='{self.url}' status={self.response.status_code} reason='{self.response.reason}' headers={h}\n"
        else:
            return f"url='{self.url}' status={self.response.status_code} reason='{self.response.reason}'"


class BaseClient:
    def __init__(self):
        self.last_url = None
        self.redirect_count = 0

        self.basedir = os.path.join(str(pathlib.Path.home()), '.financials-extension')
        os.makedirs(self.basedir, exist_ok=True)

        user_agents = [
            'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:133.0) Gecko/20100101 Firefox/133.0',
            'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:134.0) Gecko/20100101 Firefox/134.0',
            'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:135.0) Gecko/20100101 Firefox/135.0',
            'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:136.0) Gecko/20100101 Firefox/136.0',
            'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0',
        ]

        if curl_cffi_present:
            self.session = requests.Session()
            if logger.isEnabledFor(logging.DEBUG) and self.session.curl:
                self.session.curl.debug()
        else:
            self.session = requests.Session()
            self.session.headers.update({'User-Agent': random.sample(user_agents, 1)[0],
                                         'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                                         'Accept-Encoding': 'gzip, deflate',
                                         'Accept-Language': 'en-US,en;q=0.5',
                                         'Connection': 'keep-alive',
                                         'Cache-Control': 'max-age=0',
                                         })

        self.session.max_redirects = 5

    def urlopen(self, url, data=None):

        self.last_url = None

        resp = self.session.request('POST' if data else 'GET', url, data=data)

        if 400 <= resp.status_code < 500:
            if resp.headers.get('X-Cache') == 'Error from cloudfront':
                resp = self.session.request('POST' if data else 'GET', url, data=data)

        if resp.status_code >= 400:
            logger.warning("url='%s' status=%s reason='%s' headers=%s", resp.url,
                           resp.status_code, resp.reason,
                           '\n'.join(sorted(resp.headers.__str__().splitlines(), key=lambda l: l.lower())))
            raise HttpException(url, resp)

        self.redirect_count = len(resp.history)
        self.last_url = resp.url

        return resp.text

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

    def version(self):
        return requests_name + "_" + requests_version

    def curl(self):
        return curl_version

    def close(self):
        self.session.close()
