# coding: utf-8
from queue import Queue

import telegram
import telegram.ext

from inftybot import handlers
from inftybot.api.base import API
from inftybot import config
from inftybot.dispatcher import Dispatcher


def create_bot(*args, **kwargs):
    """
    Factory for bot instances

    :param kwargs:
        token: telegram bot api token

    :return:
    """
    token = kwargs.pop('token')
    bot = telegram.Bot(token=token)
    return bot


def create_dispatcher(bot, workers=1, **kwargs):
    """
    Factory for message dispatcher
    :param bot: bot instance
    :param workers: workers count
    :param kwargs: Dispatcher kwargs
    :return:
    """
    dispatcher = Dispatcher(bot, Queue(), workers=workers, **kwargs)
    register_handlers(dispatcher)
    return dispatcher


def register_handlers(dispatcher):
    """
    Registers message handlers

    Injects webhook_handler to original dispatcher object
    for handling (decode and instantiate Update objects)
    from webhook requests

    :param dispatcher: import telegram.ext.Dispatcher instance
    :return:
    """
    dispatcher.add_handler(telegram.ext.CommandHandler("start", handlers.command_handler))
    dispatcher.add_handler(telegram.ext.InlineQueryHandler(handlers.inline_query_handler))
