# coding: utf-8
import gettext

from schematics.exceptions import DataError
from slumber.exceptions import HttpClientError, HttpServerError
from telegram import InlineKeyboardButton
from telegram.ext import CommandHandler

from inftybot.intents import constants, states
from inftybot.intents.base import BaseCommandIntent, BaseIntent, AuthenticatedMixin
from inftybot.intents.exceptions import ValidationError, APIResourceError
from inftybot.intents.utils import render_model_errors

_ = gettext.gettext


CHOOSE_TYPE_KEYBOARD = [
    [
        InlineKeyboardButton("Need", callback_data=constants.TOPIC_TYPE_NEED),
        InlineKeyboardButton("Goal", callback_data=constants.TOPIC_TYPE_GOAL),
        InlineKeyboardButton("Idea", callback_data=constants.TOPIC_TYPE_IDEA)
    ],
    [
        InlineKeyboardButton("Plan", callback_data=constants.TOPIC_TYPE_PLAN),
        InlineKeyboardButton("Step", callback_data=constants.TOPIC_TYPE_STEP),
        InlineKeyboardButton("Task", callback_data=constants.TOPIC_TYPE_TASK)
    ]
]


class BaseTopicIntent(BaseIntent):
    @property
    def topic(self):
        return self.chat_data.get('topic', None)

    @topic.setter
    def topic(self, value):
        self.chat_data['topic'] = value


class TopicDoneCommandIntent(AuthenticatedMixin, BaseTopicIntent, BaseCommandIntent):
    """Sends created topic to the Infty API, resets topic creation context"""
    @classmethod
    def get_handler(cls):
        return CommandHandler("done", cls.as_callback(), pass_chat_data=True)

    def validate(self):
        topic = self.chat_data['topic']

        try:
            topic.validate()
        except DataError as e:
            errors = render_model_errors(e)
            raise ValidationError(errors)

    def handle_error(self, error):
        self.update.message.reply_text(_("Please, check this:"))
        self.update.message.reply_text(error.message)

    def handle(self, *args, **kwargs):
        topic = self.chat_data['topic']

        try:
            rv = self.api.client.topics.post(data=topic.to_native())
        except (HttpClientError, HttpServerError) as e:
            # intercept 4xx and 5xx both
            raise APIResourceError('Internal error. Please, report it')

        self.update.message.reply_text(
            _("Done. Your topic: {}".format(rv.get('url')))
        )
        return states.STATE_END
