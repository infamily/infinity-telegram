# coding: utf-8
import telegram
from telegram import Update


def render_error_list(errors):
    message_list = []

    for field, messages in errors:
        for message in messages:
            message_list.append(
                "{}: {}".format(field, message)
            )

    return message_list


def render_model_errors(error):
    return render_error_list(error.messages.items())


def update_from_dict(bot, update_dict):
    """Makes an Update object from dict"""
    if not isinstance(update_dict, Update):
        update_dict = telegram.Update.de_json(update_dict, bot)
    return update_dict


def build_menu(buttons, n_cols, header_buttons=None, footer_buttons=None):
    """
    Builds menu
    https://github.com/python-telegram-bot/python-telegram-bot/wiki/Code-snippets#build-a-menu-with-buttons
    """
    buttons = list(buttons)
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, header_buttons)
    if footer_buttons:
        menu.append(footer_buttons)
    return menu


def render_errors(errors):
    # todo: move to the intents.utils
    return "\n".join(errors)
