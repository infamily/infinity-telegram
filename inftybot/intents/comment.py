# coding: utf-8
"""
This module handles comment/reply intents
"""
import datetime
import gettext
import logging
import urllib.parse

from slumber.exceptions import HttpClientError, HttpServerError
from telegram.ext import CommandHandler, ConversationHandler, MessageHandler, Filters, BaseFilter

from inftybot import config
from inftybot.intents import states
from inftybot.intents.base import AuthenticatedMixin, BaseCommandIntent, BaseConversationIntent, CancelCommandIntent, \
    BaseMessageIntent, AuthenticationMixin
from inftybot.intents.exceptions import ValidationError, CaptchaValidationError
from inftybot.models import User


_ = gettext.gettext
logger = logging.getLogger(__name__)


class MessageParser(object):
    """Message parser with some utility methods"""
    def __init__(self, message):
        self.message = message

    def get_message_contains_topic(self):
        """
        Parses the topic message and determine if message contains the topic

        Example message:
            Goal: .:en:Test Topic

            .:en
            Hello World!

            URL: http://test.wfx.io/api/v1/topics/658/
            Reply to this message to post a comment on Infinity.
        """
        parts = self.message.strip().split('\n')

        try:
            # it is not necessary to search in the whole message
            return 'reply to this message' in parts[-1].lower()
        except IndexError:
            return False

    def get_topic_url(self):
        """
        Parses the topic message and returns the topic URL

        Example message:
            Goal: .:en:Test Topic

            .:en
            Hello World!

            URL: http://test.wfx.io/api/v1/topics/658/
            Reply to this message to post a comment on Infinity.

        So URL row should have index -2
        """
        parts = self.message.strip().split('\n')

        if len(parts) < 2:
            return None

        try:
            return parts[-2].split('URL:')[1].strip()
        except IndexError:
            return None

    def get_topic_id(self):
        topic_url = self.get_topic_url()

        try:
            return int(topic_url.strip('/').rsplit('/', 1)[-1])
        except (IndexError, TypeError):
            return None


class TopicReplyFilter(BaseFilter):
    """Filter replies to the topics sent via the bot"""
    def filter(self, message):
        reply_message = message.reply_to_message

        if not reply_message:
            return False

        parser = MessageParser(reply_message.text)
        return parser.get_message_contains_topic()


class BaseCommentIntent(AuthenticatedMixin, BaseMessageIntent):
    pass


class ReplyIntent(BaseCommentIntent):
    @classmethod
    def get_handler(cls):
        return MessageHandler(TopicReplyFilter(), cls.as_callback(), pass_chat_data=True, pass_user_data=True)

    def handle(self, *args, **kwargs):
        original_message = self.update.message.reply_to_message
        parser = MessageParser(original_message.text)
        topic_url = parser.get_topic_url()
        data = {
            'topic': topic_url,
            'text': self.update.message.text,
            # 'languages': [],
        }

        try:
            self.api.client.comments.post(data=data)
        except (HttpClientError, HttpServerError) as e:
            logger.error(e)
