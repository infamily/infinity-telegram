# coding: utf-8
from django.utils.translation import gettext
from telegram.ext import CommandHandler

from inftybot.core.intents.base import BaseCommandIntent
from inftybot.core.states import STATE_END

_ = gettext


class CancelCommandIntent(BaseCommandIntent):
    @classmethod
    def get_handler(cls):
        return CommandHandler("cancel", cls.as_callback(), pass_chat_data=True, pass_user_data=True)

    def handle(self, *args, **kwargs):
        self.update.message.reply_text(_("Canceled"))
        return STATE_END
