# coding: utf-8
from unittest import TestCase

from mock import MagicMock, patch

from inftybot.intents.inlines import parse_query, SearchTopicsInlineQuery
from inftybot.tests.base import BotMixin, patch_requests, APIMixin


class ParseQueryTestCase(TestCase):
    def test_parse_query_lang_not_provided(self):
        lang, query = parse_query('somequery')
        self.assertEqual(lang, None)
        self.assertEqual(query, 'somequery')

    def test_parse_query_lang_provided(self):
        lang, query = parse_query('en:somequery')
        self.assertEqual(lang, 'en')
        self.assertEqual(query, 'somequery')


class SearchTopicsQueryTestCase(BotMixin, APIMixin, TestCase):
    def setUp(self):
        super(SearchTopicsQueryTestCase, self).setUp()
        self.bot = self.create_bot()
        self.api = self.create_api_client()

    def create_intent(self, query):
        update = MagicMock()
        update.inline_query.query = query
        intent = SearchTopicsInlineQuery(self.bot, update, api=self.api)
        return intent

    def test_get_params_with_lang_provided(self):
        intent = self.create_intent('en:somequery')
        params = intent.get_params()
        self.assertEqual(params['lang'], 'en')
        self.assertEqual(params['search'], 'somequery')

    @patch_requests(200, '')
    def test_handle_inline_query_makes_proper_request(self, mock):
        intent = self.create_intent(query='en:somequery')
        intent.handle()
        actual_url = mock.call_args[0][0].url
        expected_url = '{}/topics/?search=somequery&lang=en'.format(self.api.base_url)
        self.assertEqual(actual_url, expected_url)
