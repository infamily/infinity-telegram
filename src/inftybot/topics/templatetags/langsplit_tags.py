# coding: utf-8
from django import template
from langsplit import splitter

from inftybot import config

register = template.Library()


@register.filter
def select_language(value, langcode=None):
    langcode = langcode or config.DEFAULT_LANGUAGE
    splitted = splitter.split(value)
    return splitted.get(langcode, value)
