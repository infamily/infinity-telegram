# coding: utf-8
import logging
from functools import wraps

from inftybot.config import TELEGRAM_BOT_TOKEN
from inftybot.core.factory import create_bot

logger = logging.getLogger(__name__)


def task(func):
    """Decorator provides configured bot object to the task function"""
    bot = create_bot(token=TELEGRAM_BOT_TOKEN)

    @wraps(func)
    def wrapper(*args, **kwargs):
        logger.debug('Run task {}, args: {}, kwargs: {}'.format(func, args, kwargs))
        result = func(bot, **kwargs)
        logger.debug('Task complete, result: {}'.format(result))
        return result

    return wrapper
