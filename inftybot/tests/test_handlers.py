# coding: utf-8
import json
from unittest import TestCase

from mock import patch

from inftybot.factory import create_bot, create_dispatcher


def load_payload():
    with open('./requests.json', 'r') as fp:
        return json.load(fp)


payload = load_payload()


class HandlerTestCase(TestCase):
    validate_token_patch = patch('telegram.bot.Bot._validate_token')
    # send_message_patch = patch('telegram.bot.Bot.send_message')
    # answer_inline_patch = patch('telegram.bot.Bot.answer_inline_query')

    def setUp(self):
        super(HandlerTestCase, self).setUp()
        self.validate_token_patch.start()
        self.bot = create_bot(token=None)
        self.dispatcher = create_dispatcher(self.bot)

    def tearDown(self):
        super(HandlerTestCase, self).tearDown()
        self.validate_token_patch.stop()


class InlineQueryTestCase(HandlerTestCase):
    def test_unknown_query_no_results(self):
        with patch('telegram.bot.Bot.answer_inline_query') as mock:
            self.dispatcher.process_update(payload.get('INLINE_QUERY_UNKNOWN_PAYLOAD'))
            results = mock.call_args[0][1]
            self.assertEqual(len(results), 0)

    def test_known_query_has_results(self):
        with patch('telegram.bot.Bot.answer_inline_query') as mock:
            self.dispatcher.process_update(payload.get('INLINE_QUERY_PAYLOAD_GOAL'))
            results = mock.call_args[0][1]
            self.assertEqual(len(results), 1)
