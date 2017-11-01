# coding: utf-8
import sys
import string

from werkzeug.utils import import_string


def get_intent_cls(value, typ):
    """
    Return proper classname for intent name (given from ```value```) with ```typ``` as capitalized postfix

    For example:
        /start, Command -> StartCommand
        /say_hello, Command -> SayHelloCommand

        hey!, Message -> HeyMessage
    """
    if value.startswith('/'):
        value = value[1:]

    words = value.split('_')
    words = [w.capitalize() for w in words]
    words = [''.join(ch for ch in w if ch not in string.punctuation) for w in words]

    return '{}{}'.format(''.join(words), typ)


def get_intent_for_command(update):
    """Return proper intent handler class for command"""
    command_module = import_string('inftybot.intents.commands')  # todo: do not hardcode module there
    command_cls = get_intent_cls(update.message.text, 'Command')
    return getattr(command_module, command_cls)


def get_intent_for_inline(update):
    """Return proper intent handler class for inline query"""
    assert update
    inline_module = import_string('inftybot.intents.inlines')  # todo: do not hardcode module there
    return getattr(inline_module, 'SearchTopicsInlineQuery')
