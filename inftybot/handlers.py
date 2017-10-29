# coding: utf-8
import telegram


def start_command_handler(bot, update):
    return {}


def inline_query_handler(bot, update):
    return {}


def common_message_handler(bot, update):
    update.message.reply_text("Hey!")
