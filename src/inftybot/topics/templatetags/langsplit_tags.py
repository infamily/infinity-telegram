# coding: utf-8
from django import template
from langsplit import splitter

from inftybot import config

register = template.Library()


@register.filter
def select_language(value, langcode=None):
    if isinstance(value, list):
        return [select_language(v) for v in value]
    langcode = langcode or config.DEFAULT_LANGUAGE
    splitted = splitter.split(value)
    if isinstance(splitted, dict):
        return splitted.get(langcode, value)
    return value
