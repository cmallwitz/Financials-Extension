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

    VOLUME = 35
    AVG_DAILY_VOL_3MOMTH = 39

    CLOSE = 90
    ADJ_CLOSE = 91

    TICKER = 101
    EXCHANGE = 102
    CURRENCY = 103
    NAME = 104
    TIMEZONE = 105

    TIMESTAMP = 999

    # TODO YAHOO fundInceptionDate

    @classmethod
    def has_value(cls, value):
        return (any(value == item.value for item in cls))
