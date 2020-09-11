import re


def is_positive_float(f):
    return type(f) == float and f > 0.0


def is_date(s):
    match = re.compile(r'^20\d\d-\d\d-\d\d$', flags=re.DOTALL).search(s)
    return match is not None
