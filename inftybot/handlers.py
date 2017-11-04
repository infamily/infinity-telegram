# coding: utf-8
from werkzeug.utils import import_string

import inftybot.intents.utils
from inftybot import config
from inftybot.utils import process_update


def command_handler(bot, update):
    update = process_update(bot, update)
    handler_cls = inftybot.intents.utils.get_intent_for_command(update)
    handler = handler_cls(bot, update)
    reply = handler.handle()
    update.message.reply_text(reply)


def inline_query_handler(bot, update):
    update = process_update(bot, update)
    handler_cls = inftybot.intents.utils.get_intent_for_inline(update)
    handler = handler_cls(bot, update)
    results = handler.handle()
    update.inline_query.answer(results, cache_time=config.INLINE_QUERY_CACHE_TIME)


def as_callback(intent_cls, **kwargs):
    cls = import_string(intent_cls)
    return cls()
