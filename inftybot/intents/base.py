# coding: utf-8
import gettext
import logging

from telegram.ext import MessageHandler, Filters, CommandHandler, CallbackQueryHandler

from inftybot.api import API
from inftybot.intents import states
from inftybot.intents.exceptions import IntentHandleException, ValidationError

logger = logging.getLogger(__name__)
_ = gettext.gettext


class BaseIntent(object):
    """Base class for intent handler"""
    def __init__(self, **kwargs):
        self.api = kwargs.pop('api', API())
        self.bot = kwargs.pop('bot', None)
        self.update = kwargs.pop('update', None)
        self.chat_data = kwargs.pop('chat_data', {})
        self.user_data = kwargs.pop('user_data', {})
        self._errors = []

    @property
    def user(self):
        return self.chat_data.get('user', None)

    @user.setter
    def user(self, value):
        self.chat_data['user'] = value

    @property
    def errors(self):
        return self._errors

    def __call__(self, *args, **kwargs):
        try:
            self.chat_data = kwargs.pop('chat_data', {})
            self.user_data = kwargs.pop('user_data', {})
            self.before_validate()
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

        def handler(bot, update, **callback_kwargs):
            kwargs = {'bot': bot, 'update': update}
            kwargs.update(init_kwargs)
            self = cls(**kwargs)
            self.bot = bot
            self.update = update
            return self(**callback_kwargs)

        return handler

    @classmethod
    def get_handler(cls):
        raise NotImplementedError

    def validate(self):
        pass

    def before_validate(self):
        pass

    def handle(self, *args, **kwargs):
        """
        This method is used as ```python-telegram-bot``` handler callback
        see: as_callback() and __call__() methods
        """
        raise NotImplementedError

    def handle_error(self, error):
        pass


class BaseInlineQuery(BaseIntent):
    def handle(self, *args, **kwargs):
        raise NotImplementedError

    @classmethod
    def get_handler(cls):
        raise NotImplementedError

    def __init__(self, **kwargs):
        super(BaseInlineQuery, self).__init__(**kwargs)
        lang, query = self.parse_query()
        self.lang = lang
        self.query = query

    def handle_error(self, error):
        raise NotImplementedError

    def parse_query(self):
        """
        Parse ```update.inline_query.query``` for lang and query parts
        :return:
        """
        return parse_query(self.update.inline_query.query)


def parse_query(query):
    """
    Parse inline query for lang and query parts
    :return:
    """
    try:
        lang, query = query.split(':', 1)
    except ValueError:
        lang = None

    return lang, query


class BaseMessageIntent(BaseIntent):
    def handle(self, *args, **kwargs):
        raise NotImplementedError

    @classmethod
    def get_handler(cls):
        raise NotImplementedError

    @classmethod
    def get_handler(cls):
        return MessageHandler(
            Filters.text, cls.as_callback(), pass_chat_data=True
        )

    def handle_error(self, error):
        self.update.message.reply_text(error.message)


class BaseCommandIntent(BaseIntent):
    def handle(self, *args, **kwargs):
        raise NotImplementedError

    @classmethod
    def get_handler(cls):
        raise NotImplementedError

    def handle_error(self, error):
        self.update.message.reply_text(error.message)


class BaseCallbackIntent(BaseIntent):
    """Base intent class for callback query (buttons, etc.)"""
    def handle(self, *args, **kwargs):
        raise NotImplementedError

    @classmethod
    def get_handler(cls):
        raise NotImplementedError

    @classmethod
    def get_handler(cls):
        return CallbackQueryHandler(
            cls.as_callback(), pass_chat_data=True
        )

    def handle_error(self, error):
        self.update.message.reply_text(error.message)


class BaseConversationIntent(BaseIntent):
    @classmethod
    def get_handler(cls):
        raise NotImplementedError

    def handle(self, *args, **kwargs):
        """No direct handling assumed"""
        pass


class CancelCommandIntent(BaseCommandIntent):
    @classmethod
    def get_handler(cls):
        return CommandHandler("cancel", cls.as_callback(), pass_chat_data=True)

    def handle(self, *args, **kwargs):
        self.update.message.reply_text(_("Canceled"))
        return states.STATE_END


class AuthenticatedMixin(BaseIntent):
    """Intent with Infty API authentication"""
    def handle(self, *args, **kwargs):
        return super(AuthenticatedMixin, self).handle()

    @classmethod
    def get_handler(cls):
        return super(AuthenticatedMixin, cls).get_handler()

    def _update_user_token(self):
        if self.user and self.user.token:
            self.set_api_authentication(self.user.token)

    def before_validate(self):
        self._update_user_token()
        super(AuthenticatedMixin, self).before_validate()

    def set_api_authentication(self, token):
        if not self.user:
            raise ValueError("No user provided")

        self.user.token = token
        self.api.user = self.user
