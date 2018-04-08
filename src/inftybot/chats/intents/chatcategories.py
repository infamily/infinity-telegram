# coding: utf-8
"""Intents for handling get/set group/channel categories set"""
from django.db.transaction import atomic
from django.utils.translation import gettext
from telegram.ext import CommandHandler

from inftybot.authentication.intents.base import AuthenticatedMixin
from inftybot.chats import utils
from inftybot.chats.models import Chat, ChatCategory
from inftybot.core.exceptions import AdminRequiredError, ValidationError, ChatNotFoundError
from inftybot.core.intents.base import BaseCommandIntent, ArgparseMixin, BuildArgumentListAction

_ = gettext


class SetCategoriesCommandIntent(AuthenticatedMixin, ArgparseMixin, BaseCommandIntent):
    command_name = "setcategories"

    @classmethod
    def get_handler(cls):
        return CommandHandler(
            cls.command_name, cls.as_callback(), pass_chat_data=True, pass_user_data=True, pass_args=True
        )

    def add_arguments(self, parser):
        parser.add_argument('chat', type=str, help='Chat @username (str) or id (int) of the community')
        parser.add_argument(
            'categories', type=str, nargs='+', action=BuildArgumentListAction,
            help='Category name or comma-separated list')
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

        if not chat:
            raise ChatNotFoundError()

        # if not utils.get_chat_is_community(self.bot, chat):
        #     raise CommunityRequiredError()

        if not utils.get_user_is_admin(self.bot, self.update.effective_user, chat):
            raise AdminRequiredError()

    @atomic
    def handle(self, *args, **kwargs):
        chat_object = utils.get_chat(self.bot, self.parsed_args.chat)
        chat_instance = Chat.objects.ensure_chat(id=chat_object.id, type=chat_object.type)
        categories = self.parsed_args.categories

        chat_instance.categories.clear()

        for category in categories:
            category_instance, __ = ChatCategory.objects.get_or_create(name=category)
            chat_instance.categories.add(category_instance)

        chat_instance.save()

        message = _("Current categories for {} ({}): {}".format(
            utils.get_chat_title(chat_object), chat_object.id,
            ", ".join(chat_instance.categories.all().values_list('name', flat=True))
        ))

        self.update.message.reply_text(message)


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

        if not chat:
            raise ChatNotFoundError()

        # if not utils.get_chat_is_community(self.bot, chat):
        #     raise CommunityRequiredError()

        if not utils.get_user_is_admin(self.bot, self.update.effective_user, chat):
            raise AdminRequiredError()

    def handle(self, *args, **kwargs):
        chat_object = utils.get_chat(self.bot, self.parsed_args.chat)
        chat_instance = Chat.objects.ensure_chat(id=chat_object.id, type=chat_object.type)
        message = _("Current categories for {} ({}): {}".format(
            utils.get_chat_title(chat_object), chat_object.id,
            ", ".join(chat_instance.categories.all().values_list('name', flat=True))
        ))

        self.update.message.reply_text(message)
