# coding: utf-8
import telegram
from telegram import Update, Chat


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


def _get_chat_id(chat):
    if isinstance(chat, Chat):
        return chat.id
    return chat


def get_chat_is_community(bot, chat):
    """Return True if chat is a community (group or channel)"""
    chat_id = _get_chat_id(chat)
    chat = bot.get_chat(chat_id)
    return chat.type in (Chat.GROUP, Chat.CHANNEL)


def get_user_is_admin(bot, user, chat):
    """Return True if user is admin of the chat"""
    chat_id = _get_chat_id(chat)
    admins = bot.get_chat_administrators(chat_id)
    return user.id in (m.user.id for m in admins)
