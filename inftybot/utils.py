# coding: utf-8
import telegram
from telegram import Update


def update_from_dict(bot, update_dict):
    """Makes an Update object from dict"""
    if not isinstance(update_dict, Update):
        update_dict = telegram.Update.de_json(update_dict, bot)
    return update_dict
