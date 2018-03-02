# coding: utf-8
# flake8: noqa
from abc import ABC
from unittest import TestCase

from mock import patch, MagicMock
from telegram import Update

from inftybot import config
from inftybot.core.dispatcher import Dispatcher, DynamoDispatcher
from inftybot.core.factory import create_dispatcher


class TestDispatcherABC(ABC):
    pass


class TestDispatcher(Dispatcher):
    pass


TestDispatcherABC.register(TestDispatcher)


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

    @patch('inftybot.core.storage.DynamoDBStorage.get')
    def test_get_user_data_from_dynamo_db(self, m):
        _ = self.dispatcher.user_data[self.user_id]
        self.assertEqual(m.call_count, 1)

    @patch('inftybot.core.storage.DynamoDBStorage.get')
    def test_get_chat_data_from_dynamo_db(self, m):
        _ = self.dispatcher.chat_data[self.user_id]
        self.assertEqual(m.call_count, 1)


class DispatcherDefaultClassFallbackTestCase(TestCase):
    def test_provided_default_dispatcher_class_is_used(self):
        config.DISPATCHER_DEFAULT_CLASS = 'src.inftybot.core.tests.test_dispatcher.TestDispatcher'

        dispatcher = create_dispatcher(MagicMock())
        self.assertIsInstance(dispatcher, TestDispatcher)
