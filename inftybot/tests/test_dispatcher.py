# coding: utf-8
from unittest import TestCase

from mock import patch, MagicMock
from telegram import Update

from inftybot.dispatcher import Dispatcher, DynamoDispatcher


class DispatcherTestCase(TestCase):
    @patch('telegram.ext.Dispatcher.process_update')
    def test_dispatcher_process_update_translate_payload_from_dict_to_Update(self, m):
        dispatcher = Dispatcher(MagicMock(), MagicMock(), 1)
        dispatcher.process_update({'update_id': 1, 'message': {}})
        args, kwargs = m.call_args
        self.assertIsInstance(args[0], Update)


class DynamoDispatcherUserDataTestCase(TestCase):
    def setUp(self):
        self.user_id = '1234567890'
        self.dispatcher = DynamoDispatcher(MagicMock(), MagicMock())

    @patch('inftybot.storage.DynamoDBStorage.get')
    def test_get_user_data_from_dynamo_db(self, m):
        _ = self.dispatcher.user_data[self.user_id]
        self.assertEqual(m.call_count, 1)

    @patch('inftybot.storage.DynamoDBStorage.get')
    def test_get_chat_data_from_dynamo_db(self, m):
        _ = self.dispatcher.chat_data[self.user_id]
        self.assertEqual(m.call_count, 1)
