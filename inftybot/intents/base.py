# coding: utf-8
from werkzeug.local import Local

from inftybot.api import API
from inftybot.intents.exceptions import IntentHandleException


local = Local()


class BaseIntent(object):
    """Base class for intent handler"""
    def __init__(self, **kwargs):
        self.api = kwargs.get('api', API())
        self.bot = kwargs.get('bot', None)
        self.update = kwargs.get('update', None)
        self.data = local

    def __call__(self, *args, **kwargs):
        try:
            self.validate()
            return self.handle(*args, **kwargs)
        except IntentHandleException as e:
            return self.handle_error(e)

    @classmethod
    def as_callback(cls, **init_kwargs):
        """Hello, django as_view()"""

        def handler(bot, update, *args, **callback_kwargs):
            kwargs = {'bot': bot, 'update': update}
            kwargs.update(init_kwargs)
            self = cls(**kwargs)
            self.bot = bot
            self.update = update
            return self(*args, **callback_kwargs)

        return handler

    @classmethod
    def get_handler(cls):
        raise NotImplementedError

    def validate(self):
        pass

    def handle(self, *args, **kwargs):
        """
        This method is used as ```python-telegram-bot``` handler callback
        see: as_callback() and __call__() methods
        """
        raise NotImplementedError

    def handle_error(self, error):
        pass
