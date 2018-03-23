# coding: utf-8
import telegram
from telegram import Chat

from inftybot.core.exceptions import ChatNotFoundError


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
    # except telegram.error.BadRequest:
    #     raise AdminRequiredError()


def get_chat_title(chat):
    return chat.title or "{} {}".format(chat.last_name, chat.first_name)


def get_chat_is_community(bot, chat):
    """Return True if chat is a community (group or channel)"""
    chat = get_chat(bot, chat)
    return chat.type in (Chat.GROUP, Chat.CHANNEL)


def get_user_is_admin(bot, user, chat):
    """Return True if user is admin of the chat"""
    if chat.type == Chat.PRIVATE:
        return True

    chat_id = _get_chat_id(chat)
    admins = bot.get_chat_administrators(chat_id)
    return user.id in (m.user.id for m in admins)
