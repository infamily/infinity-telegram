# coding: utf-8
"""Intents for handling get/set group/channel categories set"""
import telegram.error
from django.utils.translation import gettext
from telegram.ext import CommandHandler

import inftybot.chats.utils
from inftybot.authentication.intents.base import AuthenticatedMixin
from inftybot.chats.models import Chat
from inftybot.core.exceptions import CommunityRequiredError, AdminRequiredError, ValidationError, ChatNotFoundError
from inftybot.core.intents.base import BaseCommandIntent, ArgparseMixin

_ = gettext


def get_chat(bot, id_or_name):
    try:
        return inftybot.chats.utils.get_chat(bot, id_or_name)
    except telegram.error.BadRequest:
        raise AdminRequiredError()


def get_chat_storage(chat_id):
    chat, _ = Chat.objects.get_or_create(id=chat_id)
    chat.ensure_chat_data()
    return chat.chatdata


class SetCategoriesCommandIntent(AuthenticatedMixin, ArgparseMixin, BaseCommandIntent):
    command_name = "setcategories"

    @classmethod
    def get_handler(cls):
        return CommandHandler(
            cls.command_name, cls.as_callback(), pass_chat_data=True, pass_user_data=True, pass_args=True
        )

    def add_arguments(self, parser):
        parser.add_argument('chat', type=str, help='Chat @username (str) or id (int) of the community')
        parser.add_argument('categories', type=str, help='Category name or comma-separated list')
        return parser

    def before_validate(self, *args, **kwargs):
        if inftybot.chats.utils.get_chat_is_community(self.bot, self.update.effective_chat):
            message = _(
                "You should to use this command in direct chat with me. \n"
                "BTW, current group's id is: {}".format(self.update.effective_chat.id)
            )
            raise ValidationError(message)

        self.parsed_args = self.parser.parse_args(kwargs.get('args'))
        chat = get_chat(self.bot, self.parsed_args.chat)

        if not chat:
            raise ChatNotFoundError()

        if not inftybot.chats.utils.get_chat_is_community(self.bot, chat):
            raise CommunityRequiredError()

        if not inftybot.chats.utils.get_user_is_admin(self.bot, self.update.effective_user, chat):
            raise AdminRequiredError()

    def handle(self, *args, **kwargs):
        chat = get_chat(self.bot, self.parsed_args.chat)
        categories = self.parsed_args.categories.split(',')
        storage = get_chat_storage(chat.id)
        storage.data['categories'] = categories
        storage.save()
        self.update.message.reply_text(_("OK"))


class GetCategoriesCommandIntent(AuthenticatedMixin, ArgparseMixin, BaseCommandIntent):
    command_name = "getcategories"

    @classmethod
    def get_handler(cls):
        return CommandHandler(
            cls.command_name, cls.as_callback(), pass_chat_data=True, pass_user_data=True, pass_args=True
        )

    def add_arguments(self, parser):
        parser.add_argument('chat', type=str, help='Chat @username (str) or id (int) of the community')
        return parser

    def before_validate(self, *args, **kwargs):
        if inftybot.chats.utils.get_chat_is_community(self.bot, self.update.effective_chat):
            message = _(
                "You should to use this command in direct chat with me. \n"
                "BTW, current group's id is: {}".format(self.update.effective_chat.id)
            )
            raise ValidationError(message)

        self.parsed_args = self.parser.parse_args(kwargs.get('args'))
        chat = get_chat(self.bot, self.parsed_args.chat)

        if not chat:
            raise ChatNotFoundError()

        if not inftybot.chats.utils.get_chat_is_community(self.bot, chat):
            raise CommunityRequiredError()

        if not inftybot.chats.utils.get_user_is_admin(self.bot, self.update.effective_user, chat):
            raise AdminRequiredError()

    def handle(self, *args, **kwargs):
        chat = inftybot.chats.utils.get_chat(self.bot, self.parsed_args.chat)
        storage = get_chat_storage(chat.id)
        categories = storage.data.get('categories', [])
        categories_str = ', '.join(categories) if categories else 'empty'
        message = "{}: {}".format(_("CATEGORIES_LIST"), categories_str)
        self.update.message.reply_text(_(message))
