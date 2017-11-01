# coding: utf-8
import json
import os
from unittest import TestCase

from mock import patch
from telegram import User

from inftybot.api import API
from inftybot.factory import create_bot


def load_tg_updates():
    current_dir = os.path.dirname(__file__)
    requests_file = '{}/tg_updates.json'.format(current_dir)
    with open(requests_file, 'r') as fp:
        return json.load(fp)


class BotMixin(TestCase):
    validate_token_patch = patch('telegram.bot.Bot._validate_token')
    BOT_INFO = {'id': 305561733, 'is_bot': True, 'first_name': 'DummyBot', 'username': 'dummy_dummy_bot'}

    def create_bot(self):
        bot = create_bot(token=None)
        bot_info = User.de_json(self.BOT_INFO, bot)
        bot.bot = bot_info
        bot.get_me = lambda: bot_info
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
        return json.loads(self.content)


def patch_requests(response_status_code, response_content=None):
    response = MockResponse(response_status_code, response_content)
    return patch('requests.sessions.Session.send', return_value=response)


class APIMixin(TestCase):
    def create_api_client(self):
        api = API(base_url='http://example.com/api/v1')
        return api
