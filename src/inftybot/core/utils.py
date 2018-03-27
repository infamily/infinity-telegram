# coding: utf-8
import telegram
from django.template.loader import render_to_string
from telegram import Update


def render_error_list(errors):
    return render_to_string('core/error_list.html', {
        'error_list': errors,
        'errors': errors,
    })


def render_form_errors(form):
    return render_error_list(form.errors)


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
    # todo: remove this wrapper
    return render_error_list(errors)
