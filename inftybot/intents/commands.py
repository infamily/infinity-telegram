# coding: utf-8
import gettext

from telegram import InlineKeyboardMarkup
from telegram.ext import CommandHandler

from inftybot.intents import states
from inftybot.intents.base import BaseIntent


_ = gettext.gettext


class BaseCommandIntent(BaseIntent):
    def handle_error(self, error):
        self.update.message.reply_text(error.message)


class StartCommandIntent(BaseCommandIntent):
    @classmethod
    def get_handler(cls):
        return CommandHandler("start", cls.as_callback(), pass_chat_data=True)

    def handle(self, *args, **kwargs):
        self.update.message.reply_text(_("Let's start"))


class LoginCommandIntent(BaseCommandIntent):
    @classmethod
    def get_handler(cls):
        return CommandHandler("login", cls.as_callback(), pass_chat_data=True)

    def handle(self, *args, **kwargs):
        self.update.message.reply_text(_("What's your email?"))
        return states.AUTH_STATE_EMAIL


class CancelCommandIntent(BaseCommandIntent):
    @classmethod
    def get_handler(cls):
        return CommandHandler("cancel", cls.as_callback(), pass_chat_data=True)

    def handle(self, *args, **kwargs):
        self.update.message.reply_text(_("Canceled"))
        return states.STATE_END


class TopicCreateCommandIntent(BaseCommandIntent):
    """Enters topic creation context"""
    @classmethod
    def get_handler(cls):
        return CommandHandler("newtopic", cls.as_callback(), pass_chat_data=True)

    def get_keyboard(self):
        return []

    def handle(self, *args, **kwargs):
        keyboard = self.get_keyboard()
        self.update.message.reply_text(
            _("Please, choose:"), reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return states.TOPIC_STATE_TITLE


class TopicDoneCommandIntent(BaseCommandIntent):
    """Sends created topic to the Infty API, resets topic creation context"""
    @classmethod
    def get_handler(cls):
        return CommandHandler("done", cls.as_callback(), pass_chat_data=True)

    def handle(self, *args, **kwargs):
        # handle creation
        # handle editing
        # handle remove ?
        self.update.message.reply_text(
            _("Done")
        )
        return states.STATE_END
