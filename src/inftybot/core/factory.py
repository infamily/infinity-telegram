# coding: utf-8
import logging
from queue import Queue

import telegram
import telegram.ext
from werkzeug.utils import import_string

from inftybot import config
from inftybot.core.intents.base import BaseIntent

logger = logging.getLogger(__name__)


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
    dispatcher_cls_str = kwargs.pop('class', None)

    if dispatcher_cls_str:
        try:
            dispatcher_cls = import_string(dispatcher_cls_str)
        except ImportError:
            dispatcher_cls = import_string(config.DISPATCHER_DEFAULT_CLASS)
    else:
        dispatcher_cls = import_string(config.DISPATCHER_DEFAULT_CLASS)

    dispatcher = dispatcher_cls(bot, Queue(), workers=workers, **kwargs)

    if config.TELEGRAM_ERROR_HANDLER:
        error_handler = import_string(config.TELEGRAM_ERROR_HANDLER)
        dispatcher.add_error_handler(error_handler)

    register_intents(dispatcher)
    return dispatcher


def create_intent(conf_object):
    if isinstance(conf_object, dict):
        return import_string(conf_object['cls'])
    return import_string(conf_object)


def get_intents_conf():
    # todo do not hardcode it there
    return config.INTENTS


def register_intents(dispatcher):
    """
    Registers message handlers
    :param dispatcher: import telegram.ext.Dispatcher instance
    :return:
    """
    conf = get_intents_conf()

    for conf_obj in conf:
        intent_cls = create_intent(conf_obj)

        if not issubclass(intent_cls, BaseIntent):
            raise NotImplementedError

        dispatcher.add_handler(intent_cls.get_handler())
