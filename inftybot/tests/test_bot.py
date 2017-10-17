# coding: utf-8
from unittest import TestCase

from mock import patch

from inftybot.factory import create_bot


class BotFactoryTestCase(TestCase):
    @patch('telegram.bot.Bot._validate_token')
    def test_created_bot_has_webhook_handler(self, m):
        bot = create_bot(token='')
        self.assertTrue(hasattr(bot, 'webhook_handler'))
