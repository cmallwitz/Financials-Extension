#  financials.py - Pyuno/LO bridge to implement new functions for LibreOffice Calc
#
#  license: GNU LGPL
#
#  This library is free software; you can redistribute it and/or
#  modify it under the terms of the GNU Lesser General Public
#  License as published by the Free Software Foundation; either
#  version 3 of the License, or (at your option) any later version.

import datetime
import inspect
import locale
import logging
import os
import pathlib
import platform
import ssl
import sys
import time
from functools import wraps
from importlib import util
import xml.etree.ElementTree as ET

import unohelper
from com.financials.getinfo import Financials

basedir = os.path.join(str(pathlib.Path.home()), '.financials-extension')
os.makedirs(basedir, exist_ok=True)

logging.basicConfig(
    handlers=[logging.FileHandler(filename=os.path.join(basedir, 'extension.log'), encoding='utf-8', mode='a+')],
    format="%(asctime)s %(name)s %(levelname)s %(message)s",
    level=logging.INFO)

# Add current directory to import path
current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

dateutil_missing = util.find_spec("dateutil") is None
pyparsing_missing = util.find_spec("pyparsing") is None
pytz_missing = util.find_spec("pytz") is None

if dateutil_missing or pyparsing_missing or pytz_missing:
    msg = ''
    msg += ' dateutil' if dateutil_missing else ''
    msg += ' pyparsing' if pyparsing_missing else ''
    msg += ' pytz' if pytz_missing else ''
    raise Exception("THIS EXTENSION NEEDS THE FOLLOWING PYTHON 3 LIBRARIES INSTALLED:" + msg)

import dateutil.parser
import pytz
import pyparsing
import six

from datacode import Datacode
import financials_yahoo as yahoo
import financials_coinbase as coinbase
import financials_ft as ft

implementation_name = "com.financials.getinfo.python.FinancialsImpl"  # as defined in Financials.xcu
implementation_services = ("com.sun.star.sheet.AddIn",)

# Disabling SSL certificate validation as Python setup on MacOS seems to be broken
# Only reading public data so this should be safe

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context


def profile(fn):
    @wraps(fn)
    def with_profiling(*args, **kwargs):
        start = time.perf_counter()
        r = fn(*args, **kwargs)
        elapsed = time.perf_counter() - start

        with open(os.path.join(basedir, 'trace.log'), "a+", encoding="utf-8") as text_file:
            print(
                f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')} {fn.__name__} *args={args[1:]} r='{r}' {(1000 * elapsed):.3f} ms",
                file=text_file)

        return r

    return with_profiling


class FinancialsImpl(unohelper.Base, Financials):
    """Define the main class for the Financials extension """

    def __init__(self, ctx):
        self.ctx = ctx
        self.yahoo = yahoo.createInstance(ctx)
        self.coinbase = coinbase.createInstance(ctx)
        self.ft = ft.createInstance(ctx)

    @profile
    def getRealtime(self, ticker, datacode=None, source=None):

        if ticker == 'SUPPORT' or ticker == 'support':
            return self.support(datacode)

        try:
            if type(ticker) == tuple:
                return 'Cell range not allowed for ticker'

            if type(datacode) == tuple:
                return 'Cell range not allowed for datacode'

            if type(source) == tuple:
                return 'Cell range not allowed for source'

            if not ticker:
                return 'Ticker is empty'

            if not datacode:
                return 'Datacode is empty'

            try:
                dc = str(datacode).strip().upper()
                if dc in Datacode.__members__:
                    dc = Datacode[dc].value
                datacode = int(float(dc))
            except:
                return 'Datacode is invalid'

            if not Datacode.has_value(datacode):
                return 'Datacode {} not supported'.format(datacode)

            ticker = str(ticker).strip()
            source = str(source).upper()

            if source == 'YAHOO':
                s = self.yahoo.getRealtime(ticker, datacode)
            elif source == 'FT':
                s = self.ft.getRealtime(ticker, datacode)
            elif source == 'COINBASE':
                s = self.coinbase.getRealtime(ticker, datacode)
            else:
                s = 'Source \'{}\' not supported'.format(source)

        except Exception as ex:
            return str(ex)

        try:
            x = float(s)
        except:
            x = s

        return x

    @profile
    def getHistoric(self, ticker, datacode=None, date=None, source=None):

        if ticker == 'SUPPORT':
            return self.support(datacode)

        if type(ticker) == tuple:
            return 'Cell range not allowed for ticker'

        if type(datacode) == tuple:
            return 'Cell range not allowed for datacode'

        if type(date) == tuple:
            return 'Cell range not allowed for date'

        if type(source) == tuple:
            return 'Cell range not allowed for source'

        try:
            if not ticker:
                return 'Ticker is empty'

            if not datacode:
                return 'Datacode is empty'

            if not date:
                return 'Date is empty'

            try:
                dc = str(datacode).strip().upper()
                if dc in Datacode.__members__:
                    dc = Datacode[dc].value
                datacode = int(float(dc))
            except:
                return 'Datacode {} is invalid'.format(datacode)

            if not Datacode.has_value(datacode):
                return 'Datacode {} not supported'.format(datacode)

            if type(date) == float or type(date) == int:

                try:
                    offset = int(date)  # offset for 1899-12-30
                    d = dateutil.parser.parse('1899-12-30', yearfirst=True, dayfirst=False) + datetime.timedelta(days=offset)
                    d = d.date().isoformat()
                except:
                    return 'Date format not supported: {}'.format(date)
                date = d

            elif type(date) == str:

                try:
                    int(dateutil.parser.parse(date, yearfirst=True, dayfirst=False).timestamp())
                except:
                    return 'Date format not supported: \'{}\''.format(date)

            else:
                return 'Date type not supported: {} \'{}\''.format(type(date), date)

            ticker = str(ticker).strip()
            source = str(source).upper()

            if source == 'YAHOO':
                s = self.yahoo.getHistoric(str(ticker).strip(), datacode, date)
            else:
                s = 'Source \'{}\' not supported'.format(source)

        except Exception as ex:
            return str(ex)

        try:
            x = float(s)
        except:
            x = s

        return x

    @profile
    def support(self, datacode):

        version = '0.0.0'

        description_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'description.xml')
        for e in ET.parse(description_file).getroot():
            if e.tag.endswith('version'):
                version = e.attrib['value']

        s = ('ctx={}\nid(self)={}\nversion={}\nfile={}\ncwd={}\nhome={}\nuname={}\npid={}\nsys.executable={}\nsys.version={}\nsys.path={}\n' +
             'locale={}\ndefaultlocale={}\ndateutil={}\npytz={}\npyparsing={}\nsix={}\nrequests={}').format(
            self.ctx,
            id(self),
            version,
            os.path.realpath(__file__),
            os.path.realpath(os.getcwd()),
            str(pathlib.Path.home()),
            ' '.join(platform.uname()),
            os.getpid(),
            sys.executable,
            sys.version.replace("\n", " "),
            sys.path,
            locale.getlocale(),
            locale.getdefaultlocale(),
            dateutil.__version__,
            pytz.__version__,
            pyparsing.__version__,
            six.__version__,
            self.ft.version()
        )

        ld_preload = os.environ.get('LD_PRELOAD')
        if ld_preload:
            s += f"\nLD_PRELOAD={ld_preload}"

        curl_impersonate = os.environ.get('CURL_IMPERSONATE')
        if curl_impersonate:
            s += f"\nCURL_IMPERSONATE={curl_impersonate}"

        if 'curl_cffi' in self.ft.version():
            s += f"\ncurl_version=\"{self.ft.session.curl.version().decode()}\""

        if datacode:
            s = '{}\ntype(datacode)={}\nstr(datacode)={}'.format(
                s,
                type(datacode),
                str(datacode))

        return s

    def close(self):
        if self.yahoo: self.yahoo.close()
        if self.coinbase: self.coinbase.close()
        if self.ft: self.ft.close()


def createInstance(ctx):
    return FinancialsImpl(ctx)


# python loader looks for a static g_ImplementationHelper variable
g_ImplementationHelper = unohelper.ImplementationHelper()
g_ImplementationHelper.addImplementation(createInstance, implementation_name, implementation_services, )
