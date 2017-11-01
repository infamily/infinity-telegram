# coding: utf-8
from unittest import TestCase

import telegram
from mock import patch

from inftybot.tests.base import BotMixin, load_tg_updates
from inftybot import handlers

tg_updates = load_tg_updates()


class HandlerTestCase(BotMixin, TestCase):
    def setUp(self):
        super(HandlerTestCase, self).setUp()
        self.bot = self.create_bot()


class InlineQueryTestCase(HandlerTestCase):
    @patch('telegram.bot.Bot.answer_inline_query')
    def test_inline_query_handled_ok(self, mock):
        payload = tg_updates.get('INLINE_QUERY')
        handlers.inline_query_handler(self.bot, payload)
        self.assertEqual(mock.call_count, 1)


class CommandTestCase(HandlerTestCase):
    @patch('telegram.bot.Bot.send_message')
    def test_start_command_handled_ok(self, mock):
        payload = tg_updates.get('START_COMMAND')
        handlers.command_handler(self.bot, payload)
        self.assertEqual(mock.call_count, 1)
