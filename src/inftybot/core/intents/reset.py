# coding: utf-8
from django.utils.translation import gettext
from telegram.ext import CommandHandler

from contrib.telegram.ext.conversationhandler import get_conversation_storage
from inftybot.authentication.intents.base import logout
from inftybot.core.intents.base import BaseCommandIntent

_ = gettext


def reset(keys):
    conversation_storage = get_conversation_storage()

    for key in keys:
        try:
            del conversation_storage[key]
        except (KeyError, TypeError):
            pass


class ResetCommandIntent(BaseCommandIntent):
    @classmethod
    def get_handler(cls):
        return CommandHandler("reset", cls.as_callback(), pass_chat_data=True, pass_user_data=True)

    def handle(self, *args, **kwargs):
        user = self.update.effective_user
        chat = self.update.effective_chat

        storage_keys = ((chat.id,), (chat.id, user.id))
        reset(storage_keys)
        logout(self.current_user)

        self.update.message.reply_text(_("OK"))
