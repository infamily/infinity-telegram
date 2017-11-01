# coding: utf-8
from unittest import TestCase

from mock import MagicMock

from inftybot.intents import utils


class GetIntentClsTestCase(TestCase):
    def test_get_command_cls_one_word_lower(self):
        cls = utils.get_intent_cls('/test', 'Command')
        self.assertEqual(cls, 'TestCommand')

    def test_get_command_cls_underscored(self):
        cls = utils.get_intent_cls('/test_test', 'Command')
        self.assertEqual(cls, 'TestTestCommand')

    def test_get_command_cls_with_puntuation(self):
        cls = utils.get_intent_cls('/test,', 'Command')
        self.assertEqual(cls, 'TestCommand')


class GetIntentForCommandTestCase(TestCase):
    def test_return_proper_cls(self):
        update = MagicMock()
        update.message.text = '/start'
        cls = utils.get_intent_for_command(update)
        self.assertEqual(cls.__name__, 'StartCommand')


class GetIntentForInlineTestCase(TestCase):
    def test_return_proper_cls(self):
        update = MagicMock()
        update.inline_query.query = 'somequery'
        cls = utils.get_intent_for_inline(update)
        self.assertEqual(cls.__name__, 'SearchTopicsInlineQuery')
