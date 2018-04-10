# coding: utf-8
from django.test import TestCase

from inftybot.core.intents.base import ArgumentParser, BuildArgumentListAction


class ArgumentParserTestCase(TestCase):
    def setUp(self):
        super(ArgumentParserTestCase, self).setUp()
        self.parser = ArgumentParser('test')

    def test_argument_list_with_whitespaces(self):
        self.parser.add_argument('arg_1', type=str, help='Test argument')
        self.parser.add_argument(
            'arg_list', type=str, nargs='+', action=BuildArgumentListAction, help='Test agument list')
        args = self.parser.parse_args(['123456', 'value', '-', 'test', 'complete,', 'arg2'])
        self.assertEqual(args.arg_list, ['value - test complete', 'arg2'])
