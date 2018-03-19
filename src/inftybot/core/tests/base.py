# coding: utf-8
# flake8: noqa
import json
import os

from autofixture import AutoFixture
from django.test import TestCase
from mock import MagicMock, patch
from telegram import User, Update

from infinity.api.tests.base import APIMixin
from inftybot.authentication.models import ChatUser
from inftybot.chats.models import Chat
from inftybot.core.factory import create_bot
from inftybot.core.utils import update_from_dict


def create_user_from_update(bot, update, **params):
    if not isinstance(update, Update):
        update = update_from_dict(bot, update)

    user, _ = ChatUser.objects.get_or_create(id=update.effective_user.id, **params)
    user.ensure_session()
    return user


def create_chat_from_update(bot, update, **params):
    if not isinstance(update, Update):
        update = update_from_dict(bot, update)

    chat, _ = Chat.objects.get_or_create(id=update.effective_chat.id, **params)
    chat.ensure_chat_data()
    return chat


class UserMixin(TestCase):
    def setUp(self):
        super(UserMixin, self).setUp()
        self.user = AutoFixture(ChatUser, field_values={
            'email': 'email@example.com',
        }).create_one()
        session = self.user.ensure_session()
        session.session_data['token'] = 'test_token'
        session.save()


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


class BaseIntentTestCase(BotMixin, APIMixin, TestCase):
    intent_cls = None

    def setUp(self):
        super(BaseIntentTestCase, self).setUp()
        self.bot = self.create_bot()
        self.api = self.create_api_client()

    def create_intent(self, update, **kwargs):
        update = update_from_dict(self.bot, update)
        mock_update(update)
        intent = self.intent_cls(
            bot=self.bot, update=update,
            api=self.api, **kwargs
        )
        return intent


def load_json_file(filename):
    current_dir = os.path.dirname(__file__)
    path = '{}/{}'.format(current_dir, filename)
    with open(path, 'r') as fp:
        return json.load(fp)


def load_tg_updates():
    return load_json_file('./fixtures/tg_updates.json')


def load_api_responses():
    return load_json_file('./fixtures/api_responses.json')


def mock_update(update):
    update.effective_message.reply_text = MagicMock()
    return update


def mock_bot(bot):
    bot.sendPhoto = MagicMock()
    return bot
