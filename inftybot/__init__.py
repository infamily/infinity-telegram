# coding: utf-8
import logging

from telegram.error import TelegramError


logger = logging.getLogger(__name__)


def error_callback(bot, update, error):
    """
    Default TelegramError callback
    We need it because default python-telegram-bot's behavior - to log it with warning level
    """
    if isinstance(error, TelegramError):
        raise error  # raise it for more sentry verbosity
