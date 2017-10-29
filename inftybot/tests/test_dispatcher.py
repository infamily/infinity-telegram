# coding: utf-8
from unittest import TestCase

from mock import patch, MagicMock
from telegram import Update

from inftybot.dispatcher import Dispatcher
from inftybot.factory import create_bot


class DispatcherTestCase(TestCase):
    @patch('telegram.ext.Dispatcher.process_update')
    def test_dispatcher_process_update_translate_payload_from_dict_to_Update(self, m):
        dispatcher = Dispatcher(MagicMock(), MagicMock(), 1)
        dispatcher.process_update({'update_id': 1, 'message': {}})
        args, kwargs = m.call_args
        self.assertIsInstance(args[0], Update)
