# coding: utf-8
import telegram.ext

from inftybot import storage
from inftybot.utils import update_from_dict


class Dispatcher(telegram.ext.Dispatcher):
    """
    Telegram event (update) Dispatcher that converts data
    from dict to ```telegram.Update``` object before ```process_update```
    """
    def process_update(self, update):
        if isinstance(update, dict):
            update = update_from_dict(self.bot, update)
        return super(Dispatcher, self).process_update(update)


class DynamoDispatcher(Dispatcher):
    """Dispatcher that stores user & chat data to dynamodb"""
    def __init__(self, *args, **kwargs):
        super(DynamoDispatcher, self).__init__(*args, **kwargs)
        self.user_data = storage.UserDataStorage()
        self.chat_data = storage.ChatDataStorage()
