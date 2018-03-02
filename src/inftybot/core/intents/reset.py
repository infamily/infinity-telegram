# coding: utf-8
import gettext

from telegram.ext import CommandHandler

from inftybot.core.intents.base import BaseCommandIntent

_ = gettext.gettext


class ResetCommandIntent(BaseCommandIntent):
    @classmethod
    def get_handler(cls):
        return CommandHandler("reset", cls.as_callback(), pass_chat_data=True, pass_user_data=True)

    def handle(self, *args, **kwargs):
        self.user_data.clear()
        self.chat_data.clear()
        self.update.message.reply_text(_("OK"))
