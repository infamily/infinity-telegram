# coding: utf-8
import pprint

from telegram.ext import CommandHandler

from inftybot.chats.models import Chat
from inftybot.core.intents.base import BaseCommandIntent


class ChatInfoCommandIntent(BaseCommandIntent):
    command_name = "chatinfo"

    @classmethod
    def get_handler(cls):
        return CommandHandler(
            cls.command_name, cls.as_callback(), pass_chat_data=True, pass_user_data=True, pass_args=True
        )

    def handle(self, *args, **kwargs):
        chat_object = self.update.effective_chat
        Chat.objects.ensure_chat(pk=chat_object.id, typ=chat_object.type)
        printer = pprint.PrettyPrinter(indent=4)
        message = printer.pformat(chat_object.to_dict())
        self.update.effective_message.reply_text(message)
