# coding: utf-8
"""Intents for handling get/set group/channel categories set"""
import gettext

from telegram.ext import CommandHandler

from inftybot import utils
from inftybot.intents.base import BaseCommandIntent, ArgparseMixin, AuthenticatedMixin
from inftybot.intents.exceptions import CommunityRequiredError, AdminRequiredError, ValidationError
from inftybot.storage import ChatDataStorage

_ = gettext.gettext


def get_chat_storage(chat_id):
    return ChatDataStorage()[chat_id]


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

    def before_validate(self):
        if utils.get_chat_is_community(self.bot, self.update.effective_chat):
            message = _(
                "You should to use this command in direct chat with me. \n"
                "BTW, current group's id is: {}".format(self.update.effective_chat.id)
            )
            raise ValidationError(message)

        self.parsed_args = self.parser.parse_args(kwargs.get('args'))
        chat = utils.get_chat(self.bot, self.parsed_args.chat)

        if not utils.get_chat_is_community(self.bot, chat):
            raise CommunityRequiredError()

        if not utils.get_user_is_admin(self.bot, self.update.effective_user, chat):
            raise AdminRequiredError()

    def handle(self, *args, **kwargs):
        chat_id = self.parsed_args.chat
        categories = self.parsed_args.categories.split(',')
        storage = get_chat_storage(chat_id)
        storage['categories'] = categories
        storage.store()
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
        if utils.get_chat_is_community(self.bot, self.update.effective_chat):
            message = _(
                "You should to use this command in direct chat with me. \n"
                "BTW, current group's id is: {}".format(self.update.effective_chat.id)
            )
            raise ValidationError(message)

        self.parsed_args = self.parser.parse_args(kwargs.get('args'))
        chat = utils.get_chat(self.bot, self.parsed_args.chat)

        if not utils.get_chat_is_community(self.bot, chat):
            raise CommunityRequiredError()

        if not utils.get_user_is_admin(self.bot, self.update.effective_user, chat):
            raise AdminRequiredError()

    def handle(self, *args, **kwargs):
        chat_id = self.parsed_args.chat
        storage = get_chat_storage(chat_id)
        categories = storage.get('categories', [])
        categories_str = ', '.join(categories) if categories else 'empty'
        message = "CATEGORIES_LIST: {}".format(categories_str)
        self.update.message.reply_text(_(message))
