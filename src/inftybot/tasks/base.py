# coding: utf-8
import logging

from inftybot.config import TELEGRAM_BOT_TOKEN
from inftybot.core.factory import create_bot
from inftybot.core.storage import ChatDataStorage, UserDataStorage

logger = logging.getLogger(__name__)


def task(func):
    """Decorator provides configured bot object to the task function"""
    bot = create_bot(token=TELEGRAM_BOT_TOKEN)
    chat_storage = ChatDataStorage()
    user_storage = UserDataStorage()

    def wrapper(*args, **kwargs):
        kwargs.update({'bot': bot, 'chat_storage': chat_storage, 'user_storage': user_storage})
        logger.debug('Run task {}, args: {}, kwargs: {}'.format(func, args, kwargs))
        result = func(*args, **kwargs)
        logger.debug('Task complete, result: {}'.format(result))
        return result

    return wrapper
