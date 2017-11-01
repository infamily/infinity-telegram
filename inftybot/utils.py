# coding: utf-8
import telegram
from telegram import Update


def process_update(bot, update):
    """Makes an Update object from dict"""
    if not isinstance(update, Update):
        update = telegram.Update.de_json(update, bot)
    return update
