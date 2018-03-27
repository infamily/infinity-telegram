# coding: utf-8
import logging
from queue import Queue

from django.conf import settings
from werkzeug.utils import import_string

from inftybot import config
from inftybot.core.intents.base import BaseIntent

logger = logging.getLogger(__name__)


def create_bot(**extra_params):
    """
    Factory for bot instance
    :return:
    """
    cls_str = settings.TELEGRAM_BOT_CLASS['class']
    cls = import_string(cls_str)
    params = settings.TELEGRAM_BOT_CLASS['params']
    params.update(extra_params)
    return cls(**params)


def create_dispatcher(bot, **extra_params):
    """
    Factory for message dispatcher
    :return:
    """
    cls_str = settings.TELEGRAM_BOT_DISPATCHER['class']
    cls = import_string(cls_str)
    params = settings.TELEGRAM_BOT_DISPATCHER['params']
    params.update(extra_params)

    instance = cls(bot, Queue(), **params)

    if config.TELEGRAM_ERROR_HANDLER:
        error_handler = import_string(config.TELEGRAM_ERROR_HANDLER)
        instance.add_error_handler(error_handler)

    register_intents(instance)
    return instance


def create_intent(conf_object):
    if isinstance(conf_object, dict):
        return import_string(conf_object['class'])
    return import_string(conf_object)


def get_intents_conf():
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
