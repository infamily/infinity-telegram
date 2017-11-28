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
from inftybot.models import Topic


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
    def before_validate(self):
        # todo load topic from db or from memory (new topic)
        # self.chat_data.setdefault('topic', Topic())
        # super(EditTopicIntent, self).before_validate()
        topic = Topic()

        topic.title = 'title'
        topic.body = 'body'
        topic.type = constants.TOPIC_TYPE_TASK

        self.chat_data.setdefault('topic', topic)

    def validate(self):
        if 'topic' not in self.chat_data:
            raise ValidationError(_("Sorry, I've missed the essence :( Please, report it"))


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
