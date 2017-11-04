# coding: utf-8
import gettext

from telegram.ext import CommandHandler

from inftybot.intents.base import BaseIntent
from inftybot.intents.states import AUTH_STATE_EMAIL

_ = gettext.gettext


class BaseCommandIntent(BaseIntent):
    def handle_error(self, error):
        self.update.message.reply_text(error.message)


class StartCommandIntent(BaseCommandIntent):
    @classmethod
    def get_handler(cls):
        return CommandHandler("start", cls.as_callback(), pass_chat_data=True)

    def handle(self, *args, **kwargs):
        self.update.message.reply_text("Let's start")


class LoginCommandIntent(BaseCommandIntent):
    @classmethod
    def get_handler(cls):
        return CommandHandler("login", cls.as_callback(), pass_chat_data=True)

    def handle(self, *args, **kwargs):
        self.update.message.reply_text(_("What's your email?"))
        return AUTH_STATE_EMAIL


class CancelCommandIntent(BaseCommandIntent):
    @classmethod
    def get_handler(cls):
        return CommandHandler("cancel", cls.as_callback(), pass_chat_data=True)

    def handle(self, *args, **kwargs):
        self.update.message.reply_text(_("Canceled"))
        return -1
