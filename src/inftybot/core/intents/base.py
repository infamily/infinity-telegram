# coding: utf-8
import argparse
import gettext
import logging

from django.utils.functional import cached_property
from telegram import InlineKeyboardButton
from telegram.ext import MessageHandler, Filters, CallbackQueryHandler

import inftybot.core.constants
import inftybot.core.states
from infinity.api.base import API
from infinity.api.pagination import APIResponsePaginator
from inftybot.authentication.models import ChatUser, User
from inftybot.chats.models import Chat
from inftybot.chats.utils import get_chat_is_community, get_user_is_admin
from inftybot.core.exceptions import IntentHandleException, ValidationError, AdminRequiredError, \
    CommunityRequiredError
from inftybot.core.signals import handle_success
from inftybot.core.utils import build_menu

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
        super().__init__()
        self.instantiate()

    @cached_property
    def current_user(self):
        return self.get_current_user()

    @cached_property
    def current_chat(self):
        return self.get_current_chat()

    def get_current_user(self):
        """Returns current user model instance based on Update data"""
        instance, _ = ChatUser.objects.get_or_create(pk=self.update.effective_user.id)
        return instance

    def get_current_chat(self):
        """Returns current chat model instance based on Update data"""
        instance, _ = Chat.objects.get_or_create(pk=self.update.effective_chat.id)
        return instance

    def set_user_TODO_REMOVE(self, user):
        if isinstance(user, User):
            data = user.to_native()
        else:
            data = user
        self.user_data.update(data)

    @property
    def errors(self):
        return self._errors

    def __call__(self, *args, **kwargs):
        logger.debug('Run handler <{}>'.format(
            self.__class__.__name__,
        ))

        # todo: maybe set the value only here, in the __call__ and to remove it from __init__ ?
        self.chat_data = kwargs.pop('chat_data', self.chat_data)
        self.user_data = kwargs.pop('user_data', self.user_data)

        try:
            self.before_validate(*args, **kwargs)
        except IntentHandleException as e:
            return self.handle_error(e)

        try:
            self.validate(*args, **kwargs)
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

    def validate(self, *args, **kwargs):
        pass

    def before_validate(self, *args, **kwargs):
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
        logger.error('Unhandled error in the intent {}: {}'.format(self.__class__, error))
        pass

    @classmethod
    def create_from_intent(cls, intent, **kwargs):
        instance_kwargs = {
            'api': intent.api,
            'bot': intent.bot,
            'update': intent.update,
            'user_data': intent.user_data,
            'chat_data': intent.chat_data,
        }
        instance_kwargs.update(**kwargs)
        instance = cls(**instance_kwargs)
        return instance


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
        self.bot.send_message(chat_id=self.update.effective_chat.id, text=error.message)


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
        self.bot.send_message(
            chat_id=self.update.callback_query.message.chat_id,
            text=error.message,
        )

    def get_choose(self):
        return self.update.callback_query.data


class BaseConversationIntent(BaseIntent):
    @classmethod
    def get_handler(cls):
        raise NotImplementedError

    def handle(self, *args, **kwargs):
        """No direct handling assumed"""
        pass


class CommunityRequiredMixin(BaseIntent):
    def before_validate(self):
        if not get_chat_is_community(self.bot, self.update.effective_chat):
            raise CommunityRequiredError()
        super(CommunityRequiredMixin, self).before_validate()


class AdminRequiredMixin(BaseIntent):
    def before_validate(self):
        if not get_user_is_admin(self.bot, self.update.effective_user, self.update.effective_chat):
            raise AdminRequiredError()
        super(AdminRequiredMixin, self).before_validate()


class ObjectListKeyboardMixin(BaseIntent, APIResponsePaginator):
    """
    Mixin is used in ```Intents```.
    Handles paginated data retrieved from API
    """

    def get_current_page(self):
        return int(self.chat_data.get('current_page', 1))

    def set_current_page(self, value):
        self.chat_data['current_page'] = int(value) or 1

    def filter_list(self, lst):
        """
        Returns list ```lst``` filtered some way
        Needed, for example, to exclude current (choosen) item from the whole list
        Returns the same list ```lst``` by default but can be redefined
        """
        return lst

    @staticmethod
    def format_object(obj):
        """
        Formats every item in the ```self.iterable``` when putting it as keyboard button text
        """
        return str(obj)

    def get_keyboard(self, column_count=2):
        """
        Returns TG bot's keyboard splitted on ```column_count``` columns
        Keyboard content will be populated from ```self.iterable``` object
        :param column_count:
        :return:
        """
        if not self.iterable:
            self.iterable = self.fetch()

        buttons, header_buttons, footer_buttons = [], [], []

        for obj in self.filter_list(self.iterable):
            buttons.append(
                InlineKeyboardButton(
                    self.format_object(obj),
                    callback_data=obj.id or obj.url,
                )
            )

        if self.has_prev_page:
            footer_buttons.append(
                InlineKeyboardButton(
                    "<<", callback_data=inftybot.core.constants.PREV_PAGE,
                )
            )

        if self.has_next_page:
            footer_buttons.append(
                InlineKeyboardButton(
                    ">>", callback_data=inftybot.core.constants.NEXT_PAGE,
                )
            )

        return build_menu(
            buttons, column_count, header_buttons=header_buttons, footer_buttons=footer_buttons
        )


class ArgumentParser(argparse.ArgumentParser):
    def __init__(self, *args, **kwargs):
        kwargs['add_help'] = False  # turn -h key off
        super(ArgumentParser, self).__init__(*args, **kwargs)

    def exit(self, status=0, message=None):
        """Dummy method for make sure process won't exit"""
        pass

    def error(self, message):
        message = "{}\n\n{}".format(message, self.format_help())
        raise ValidationError(message)


class ArgparseMixin(BaseCommandIntent):
    command_name = None

    def __init__(self, **kwargs):
        super(ArgparseMixin, self).__init__(**kwargs)
        parser = self.create_parser()
        self.add_arguments(parser)
        self.parser = parser
        self.parsed_args = None

    def create_parser(self):
        return ArgumentParser(self.command_name)

    def add_arguments(self, parser):
        pass
