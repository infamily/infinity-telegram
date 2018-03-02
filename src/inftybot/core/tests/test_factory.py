# coding: utf-8
# flake8: noqa
from unittest import TestCase

from inftybot.core.factory import create_intent
from inftybot.core.intents.base import BaseIntent


class TestIntent(BaseIntent):
    def handle(self, *args, **kwargs):
        pass

    @classmethod
    def get_handler(cls):
        pass


class CreateIntentTestCase(TestCase):
    def test_create_from_string(self):
        str_conf = 'inftybot.core.tests.test_factory.TestIntent'
        intent = create_intent(str_conf)
        self.assertIsInstance(intent, BaseIntent.__class__)

    def test_create_from_dict(self):
        dict_conf = {
            'cls': 'inftybot.authentication.intents.login.LoginConversationIntent',
        }
        intent = create_intent(dict_conf)
        self.assertIsInstance(intent, BaseIntent.__class__)
