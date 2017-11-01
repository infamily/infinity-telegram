# coding: utf-8
from inftybot.api import API


class BaseIntent(object):
    """Base class for intent handler"""
    def __init__(self, bot, update, **kwargs):
        self.api = kwargs.get('api', API())
        self.bot = bot
        self.update = update

    def handle(self):
        raise NotImplementedError
