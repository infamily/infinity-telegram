# coding: utf-8
# flake8: noqa
import json
import os
from unittest import TestCase

from mock import patch, MagicMock
from telegram import User

from inftybot.factory import create_bot


def load_json_file(filename):
    current_dir = os.path.dirname(__file__)
    path = '{}/{}'.format(current_dir, filename)
    with open(path, 'r') as fp:
        return json.load(fp)


def load_tg_updates():
    return load_json_file('tg_updates.json')


def load_api_responses():
    return load_json_file('api_responses.json')


class BotMixin(TestCase):
    validate_token_patch = patch('telegram.bot.Bot._validate_token')
    BOT_INFO = {'id': 305561733, 'is_bot': True, 'first_name': 'DummyBot', 'username': 'dummy_dummy_bot'}

    def create_bot(self):
        bot = create_bot(token=None)
        bot_info = User.de_json(self.BOT_INFO, bot)
        bot.bot = bot_info
        bot.get_me = lambda: bot_info
        mock_bot(bot)
        return bot

    def setUp(self):
        super(BotMixin, self).setUp()
        self.validate_token_patch.start()

    def tearDown(self):
        super(BotMixin, self).tearDown()
        self.validate_token_patch.stop()


class MockResponse(object):
    def __init__(self, status_code, content=None, headers=None):
        self.content = content
        self.status_code = status_code
        self.headers = headers or {}

    def json(self):
        if isinstance(self.content, dict):
            return self.content
        return json.loads(self.content)


def mock_update(update):
    update.message.reply_text = MagicMock()
    return update


def mock_bot(bot):
    bot.sendPhoto = MagicMock()
    return bot
