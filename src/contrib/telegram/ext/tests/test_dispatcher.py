# coding: utf-8
# flake8: noqa
from abc import ABC
from unittest import TestCase

from mock import patch, MagicMock
from telegram import Update

from contrib.telegram.ext.dispatcher import Dispatcher


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
