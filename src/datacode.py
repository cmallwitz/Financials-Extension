#  datacode.py
#
#  license: GNU LGPL
#
#  This library is free software; you can redistribute it and/or
#  modify it under the terms of the GNU Lesser General Public
#  License as published by the Free Software Foundation; either
#  version 3 of the License, or (at your option) any later version.

from enum import Enum, unique

@unique
class Datacode(Enum):

    PREV_CLOSE = 5
    OPEN = 6
    CHANGE = 7
    LAST_PRICE_DATE = 8
    LAST_PRICE_TIME = 10
    CHANGE_IN_PERCENT = 11

    LOW = 14
    HIGH = 16

    LAST_PRICE = 21

    BID = 22
    ASK = 25
    BIDSIZE = 30
    ASKSIZE = 31

    HIGH_52_WEEK = 24
    LOW_52_WEEK = 26
    MARKET_CAP = 27

    VOLUME = 35
    AVG_DAILY_VOL_3MONTH = 39

    BETA = 67
    EPS = 68
    PE_RATIO = 69
    DIV = 70
    DIV_YIELD = 71
    EX_DIV_DATE = 72
    PAYOUT_RATIO = 73
    EXPIRY_DATE = 74
    SHARES_OUT = 75
    FREE_FLOAT = 76
    SETTLEMENT_DATE = 77

    CLOSE = 90
    ADJ_CLOSE = 91

    SECTOR = 98
    INDUSTRY = 99

    TICKER = 101
    EXCHANGE = 102
    CURRENCY = 103
    NAME = 104
    TIMEZONE = 105

    TIMESTAMP = 999

    @classmethod
    def has_value(cls, value):
        return any(value == item.value for item in cls)
