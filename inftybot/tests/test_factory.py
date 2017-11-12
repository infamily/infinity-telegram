# coding: utf-8
from unittest import TestCase

from mock import patch, MagicMock
from telegram import Update

from inftybot.factory import create_intent
from inftybot.intents.base import BaseIntent


class TestIntent(BaseIntent):
    def handle(self, *args, **kwargs):
        pass

    @classmethod
    def get_handler(cls):
        pass


class CreateIntentTestCase(TestCase):
    def test_create_from_string(self):
        str_conf = 'inftybot.tests.test_factory.TestIntent'
        intent = create_intent(str_conf)
        self.assertIsInstance(intent, BaseIntent.__class__)

    def test_create_from_dict(self):
        dict_conf = {
            'cls': 'inftybot.intents.login.LoginConversationIntent',
        }
        intent = create_intent(dict_conf)
        self.assertIsInstance(intent, BaseIntent.__class__)
