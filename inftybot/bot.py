# coding: utf-8
import telegram
from . import handlers


def create_bot(*args, **kwargs):
    """
    Factory for bot instances

    Injects webhook_handler to original bot object for handling webhook requests from external web server
    :param kwargs:
        token: telegram bot api token

    :return:
    """
    token = kwargs.pop('token')
    bot = telegram.Bot(token=token)
    setattr(bot, 'webhook_handler', handlers.webhook_handler)
    return bot
