# coding: utf-8
import telegram
import telegram.error
from telegram import Update, Chat

from inftybot.intents.exceptions import ChatNotFoundError


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
    if isinstance(chat, str):
        try:
            return int(chat)
        except ValueError:
            pass

        if not chat.startswith('@'):
            return '@{}'.format(chat)
        return chat
    raise ValueError("Undefined chat argument")


def get_chat(bot, chat):
    """Return chat by its id or name"""
    if isinstance(chat, Chat):
        return chat
    chat_id = _get_chat_id(chat)
    try:
        return bot.get_chat(chat_id)
    except telegram.error.BadRequest:
        raise ChatNotFoundError()


def get_chat_is_community(bot, chat):
    """Return True if chat is a community (group or channel)"""
    chat = get_chat(bot, chat)
    return chat.type in (Chat.GROUP, Chat.CHANNEL)


def get_user_is_admin(bot, user, chat):
    """Return True if user is admin of the chat"""
    chat_id = _get_chat_id(chat)
    admins = bot.get_chat_administrators(chat_id)
    return user.id in (m.user.id for m in admins)
