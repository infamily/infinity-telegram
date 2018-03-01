# coding: utf-8
from inftybot.config import TELEGRAM_BOT_TOKEN
from inftybot.factory import create_bot
from inftybot.storage import ChatDataStorage, UserDataStorage


def task(func):
    """Decorator provides configured bot object to the task function"""
    bot = create_bot(token=TELEGRAM_BOT_TOKEN)
    chat_storage = ChatDataStorage()
    user_storage = UserDataStorage()

    def wrapper(*args, **kwargs):
        kwargs.update({'bot': bot, 'chat_storage': chat_storage, 'user_storage': user_storage})
        result = func(*args, **kwargs)
        return result
    return wrapper
