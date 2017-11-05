# coding: utf-8
import logging

from inftybot.api import API
from inftybot.intents.exceptions import IntentHandleException, ValidationError

logger = logging.getLogger(__name__)


class BaseIntent(object):
    """Base class for intent handler"""
    def __init__(self, **kwargs):
        self.api = kwargs.pop('api', API())
        self.bot = kwargs.pop('bot', None)
        self.update = kwargs.pop('update', None)
        self.kwargs = kwargs
        self._errors = []

    @property
    def errors(self):
        return self._errors

    @property
    def chat_data(self):
        return self.kwargs.get('chat_data', {})

    @property
    def user_data(self):
        return self.kwargs.get('user_data', {})

    def __call__(self, *args, **kwargs):
        try:
            self.validate()
            return self.handle(*args, **kwargs)
        except ValidationError as e:
            self._errors.append(e)
            return self.handle_error(e)
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
            self.kwargs = callback_kwargs
            return self()

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
