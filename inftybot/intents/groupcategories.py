# coding: utf-8
"""Intents for handling get/set group/channel categories set"""
import gettext

from telegram.ext import CommandHandler

from inftybot import utils
from inftybot.intents.base import BaseCommandIntent, ArgparseMixin, AuthenticatedMixin
from inftybot.intents.exceptions import CommunityRequiredError, AdminRequiredError, ValidationError

_ = gettext.gettext


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
        if utils.get_chat_is_community(self.bot, self.update.effective_chat):
            self.update.message.reply_text(
                _("You should to use this command in direct chat with me. \nBTW, current group's id is: {}".format(
                    self.update.effective_chat.id))
            )
            return

    def validate(self, *args, **kwargs):
        self.parsed_args = self.parser.parse_args(kwargs.get('args'))
        chat = utils.get_chat(self.bot, self.parsed_args.chat)

        if not utils.get_chat_is_community(self.bot, chat):
            raise CommunityRequiredError()

        if not utils.get_user_is_admin(self.bot, self.update.effective_user, chat):
            raise AdminRequiredError()

    def handle(self, *args, **kwargs):
        self.update.message.reply_text(_("OK"))


class GetCategoriesCommandIntent(AuthenticatedMixin, ArgparseMixin, BaseCommandIntent):
    command_name = "getcategories"
    required_args = ["name_or_id"]

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
        if utils.get_chat_is_community(self.bot, self.update.effective_chat):
            self.update.message.reply_text(
                _("You should to use this command in direct chat with me. \nBTW, current group's id is: {}".format(
                    self.update.effective_chat.id))
            )
            return

    def validate(self, *args, **kwargs):
        self.parsed_args = self.parser.parse_args(kwargs.get('args'))
        chat = utils.get_chat(self.bot, self.parsed_args.chat)

        if not utils.get_chat_is_community(self.bot, chat):
            raise CommunityRequiredError()

        if not utils.get_user_is_admin(self.bot, self.update.effective_user, chat):
            raise AdminRequiredError()

    def handle(self, *args, **kwargs):
        self.update.message.reply_text(_("OK"))
