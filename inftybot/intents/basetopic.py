# coding: utf-8
import gettext

from schematics.exceptions import DataError, ValidationError as SValidationError
from slumber.exceptions import HttpClientError, HttpServerError
from telegram import InlineKeyboardButton
from telegram.ext import CommandHandler

from inftybot.intents import constants, states
from inftybot.intents.base import BaseCommandIntent, BaseIntent, AuthenticatedMixin
from inftybot.intents.exceptions import ValidationError, APIResourceError
from inftybot.intents.utils import render_model_errors
from inftybot.models import Topic
from inftybot.utils import render_errors

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
    def reset_topic(self):
        del self.chat_data['topic']

    def set_topic(self, topic):
        if isinstance(topic, Topic):
            data = topic.to_native()
        else:
            data = topic

        self.chat_data['topic'] = data

    def get_topic(self):
        data = self.chat_data.get('topic')
        return Topic.from_native(data) if data else None


class TopicDoneCommandIntent(AuthenticatedMixin, BaseTopicIntent, BaseCommandIntent):
    """Sends created topic to the Infty API, resets topic creation context"""
    @classmethod
    def get_handler(cls):
        return CommandHandler("done", cls.as_callback(), pass_chat_data=True, pass_user_data=True)

    def validate(self):
        topic = self.get_topic()

        try:
            topic.validate()
        except (DataError, SValidationError) as e:
            errors = render_model_errors(e)
            raise ValidationError(errors)

    def handle_error(self, error):
        if isinstance(error.message, list):
            message = render_errors(error.message)
        else:
            message = error.message

        message = "\n\n".join((_("There are errors :/"), message))

        self.update.message.reply_text(message)

    def handle(self, *args, **kwargs):
        topic = self.get_topic()

        if topic.id:
            method = self.api.client.topics(int(topic.id)).put
        else:
            method = self.api.client.topics.post

        try:
            rv = method(data=topic.to_native())
        except (HttpClientError, HttpServerError) as e:
            # intercept 4xx and 5xx both
            raise APIResourceError('Internal error. Please, report it')
        else:
            self.reset_topic()

        self.update.message.reply_text(
            _("Done. Your topic: {}".format(rv.get('url')))
        )

        return states.STATE_END
