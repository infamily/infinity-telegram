# coding: utf-8
from django.utils.translation import gettext
from telegram.ext import CommandHandler

from inftybot.core.intents.base import BaseCommandIntent

_ = gettext


class StartCommandIntent(BaseCommandIntent):
    @classmethod
    def get_handler(cls):
        return CommandHandler("start", cls.as_callback(), pass_chat_data=True, pass_user_data=True)

    def handle(self, *args, **kwargs):
        self.update.message.reply_text(_("Let's start. Use /login to begin."))
