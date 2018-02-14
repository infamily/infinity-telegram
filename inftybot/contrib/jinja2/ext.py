# coding: utf-8
from jinja2.ext import Extension


def split(value, split_char=None):
    """Splits string `value` by `split_char`"""
    if not value:
        return []
    return value.split(split_char)


def strip(values, strip_chars=None):
    """Strip every value in values for `stip_chars`"""
    if not isinstance(values, (list, tuple, set)):
        values = [values]
    return [v.strip(strip_chars) for v in values]


def prepend(values, prepend_char):
    """Prepends every string in values with wrap_char and returns resulting list"""
    return ['{}{}'.format(prepend_char, v) for v in values]


def exclude(values, exclude_value):
    """Exclude `exclude_value` from `values`"""
    return filter(lambda v: v != exclude_value, values)


class StringExtension(Extension):
    def __init__(self, environment):
        super(StringExtension, self).__init__(environment)
        environment.filters['split'] = split
        environment.filters['strip'] = strip
        environment.filters['prepend'] = prepend
        environment.filters['exclude'] = exclude
