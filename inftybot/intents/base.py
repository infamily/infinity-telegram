# coding: utf-8
import datetime
import gettext
import logging

from telegram.ext import MessageHandler, Filters, CommandHandler, CallbackQueryHandler

from inftybot.api import API
from inftybot.intents import states
from inftybot.intents.exceptions import IntentHandleException, ValidationError, AuthenticationError
from inftybot.intents.signals import handle_success
from inftybot.models import User

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
        self.instantiate()

    @property
    def user(self):
        data = self.chat_data.get('user', None)
        return User.from_native(data)

    def set_user(self, user):
        if isinstance(user, User):
            data = user.to_native()
        else:
            data = user
        self.chat_data['user'] = data

    @property
    def errors(self):
        return self._errors

    def __call__(self, *args, **kwargs):
        self.chat_data = kwargs.pop('chat_data', {})
        self.user_data = kwargs.pop('user_data', {})

        try:
            self.before_validate()
        except IntentHandleException as e:
            return self.handle_error(e)

        try:
            self.validate()
        except ValidationError as e:
            self._errors.append(e)
            return self.handle_error(e)

        self.before_handle()

        try:
            return_value = self.handle(*args, **kwargs)
        except IntentHandleException as e:
            return self.handle_error(e)
        else:
            handle_success.send(self, return_value=return_value)
            return return_value

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

    def instantiate(self):
        """Setup method"""
        pass

    def validate(self):
        pass

    def before_validate(self):
        # todo change before_validate to instantiate
        pass

    def before_handle(self):
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
        return MessageHandler(
            Filters.text, cls.as_callback(), pass_chat_data=True, pass_user_data=True
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
        return CallbackQueryHandler(
            cls.as_callback(), pass_chat_data=True, pass_user_data=True
        )

    def handle_error(self, error):
        self.bot.sendMessage(
            chat_id=self.update.callback_query.message.chat_id,
            text=error.message,
        )


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
        return CommandHandler("cancel", cls.as_callback(), pass_chat_data=True, pass_user_data=True)

    def handle(self, *args, **kwargs):
        self.update.message.reply_text(_("Canceled"))
        return states.STATE_END


class AuthenticationMixin(BaseIntent):
    """Adds set_api_authentication method"""
    def update_user_data(self, user):
        """
        Update current user_data from ```self.chat_data['user']``` and + authenticated_at
        """
        user_data = user.to_native()
        user_data['authenticated_at'] = datetime.datetime.utcnow().isoformat()
        self.user_data.update(user_data)

    def authenticate(self, user):
        if not user.token:
            raise AuthenticationError("Please, /login first")
        self.update_user_data(user)
        self.set_api_authentication(user)

    def set_api_authentication(self, user):
        self.api.user = user


class AuthenticatedMixin(AuthenticationMixin):
    """
    Intent with Infty API authentication
    Checks current user and its token
    """
    def is_authenticated(self):
        return self.api.is_authenticated

    def before_validate(self):
        super(AuthenticatedMixin, self).before_validate()
        self.authenticate(self.user)
