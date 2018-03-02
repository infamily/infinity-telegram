# coding: utf-8
# flake8: noqa
from unittest import TestCase

from inftybot.comments.intents.comment import MessageParser


class MessageParserTestCase(TestCase):
    def test_message_contains_topic_true(self):
        message = """
        Goal: .:en:Test Topic

        .:en
        Hello World!

        URL: http://test.wfx.io/api/v1/topics/658/
        Reply to this message to post a comment on Infinity.        
        """

        parser = MessageParser(message)
        self.assertTrue(parser.get_message_contains_topic())

    def test_message_contains_topic_false(self):
        message = """
        Goal: .:en:Test Topic

        .:en
        Hello World!
        """

        parser = MessageParser(message)
        self.assertFalse(parser.get_message_contains_topic())

    def test_get_topic_id_returns_correct_value_with_trailing_slash(self):
        message = """
        Goal: .:en:Test Topic

        .:en
        Hello World!

        URL: http://test.wfx.io/api/v1/topics/658/
        Reply to this message to post a comment on Infinity.        
        """

        parser = MessageParser(message)
        self.assertEqual(parser.get_topic_id(), 658)

    def test_get_topic_id_returns_correct_value_without_trailing_slash(self):
        message = """
        Goal: .:en:Test Topic

        .:en
        Hello World!

        URL: http://test.wfx.io/api/v1/topics/658
        Reply to this message to post a comment on Infinity.        
        """

        parser = MessageParser(message)
        self.assertEqual(parser.get_topic_id(), 658)
