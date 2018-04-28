#  financials.py - Pyuno/LO bridge to implement new functions for LibreOffice Calc
#
#  license: GNU LGPL
#
#  This library is free software; you can redistribute it and/or
#  modify it under the terms of the GNU Lesser General Public
#  License as published by the Free Software Foundation; either
#  version 3 of the License, or (at your option) any later version.

import datetime
import dateutil.parser
import inspect
import os
import sys

import pathlib
import platform

import unohelper

from com.financials.getinfo import Financials

# Add current directory to import path
current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from datacode import Datacode
import google2 as google
import yahoo

implementation_name = "com.financials.getinfo.python.FinancialsImpl"  # as defined in Financials.xcu
implementation_services = ("com.sun.star.sheet.AddIn",)


class FinancialsImpl(unohelper.Base, Financials):
    """Define the main class for the Financials extension """

    def __init__(self, ctx):
        self.ctx = ctx
        self.google = google.createInstance(ctx)
        self.yahoo = yahoo.createInstance(ctx)

    def getRealtime(self, ticker, datacode=None, source=None):

        if ticker == 'SUPPORT':
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
                datacode = int(float(str(datacode).strip()))
            except:
                return 'Datacode is not a number'

            if not Datacode.has_value(datacode):
                return 'Datacode {} not supported'.format(datacode)

            ticker = str(ticker).strip()
            source = str(source).upper()

            if source == 'GOOGLE':
                s = self.google.getRealtime(ticker, datacode)
            elif source == 'YAHOO':
                s = self.yahoo.getRealtime(ticker, datacode)
            else:
                s = 'Source \'{}\' not supported'.format(source)

        except Exception as ex:
            return str(ex)

        try:
            x = float(s)
        except:
            x = s

        return x

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
                datacode = int(float(str(datacode).strip()))
            except:
                return 'Datacode {} is not a number'.format(datacode)

            if not Datacode.has_value(datacode):
                return 'Datacode {} not supported'.format(datacode)

            if type(date) == float or type(date) == int:

                try:
                    offset = int(date) # offset for 1899-12-30
                    d = dateutil.parser.parse('1899-12-30') + datetime.timedelta(days=offset)
                    d = d.date().isoformat()
                except:
                    return 'Date format not supported: {}'.format(date)
                date = d

            elif type(date) == str:

                try:
                    int(dateutil.parser.parse(date).strftime('%s'))
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

    def support(self, datacode):

        s = 'ctx={}\nid(self)={}\npid={}\nuname={}\nsys.executable={}\nsys.version={}\nhome={}'.format(
            self.ctx,
            id(self),
            os.getpid(),
            ' '.join(platform.uname()),
            sys.executable,
            sys.version.replace("\n", " "),
            str(pathlib.Path.home()),
            type(datacode),
            str(datacode))

        if datacode:
            s = '{}\ntype(datacode)={}\nstr(datacode)={}'.format(
                s,
                type(datacode),
                str(datacode))

        return s

def createInstance(ctx):
    return FinancialsImpl(ctx)


# pythonloader looks for a static g_ImplementationHelper variable
g_ImplementationHelper = unohelper.ImplementationHelper()
g_ImplementationHelper.addImplementation(createInstance, implementation_name, implementation_services, )
