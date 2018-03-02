# coding: utf-8
import gettext
import logging

from schematics.exceptions import DataError, ValidationError as SValidationError
from slumber.exceptions import HttpClientError, HttpServerError
from telegram import InlineKeyboardButton, ParseMode
from telegram.ext import CommandHandler

import inftybot.core.states
import inftybot.topics.constants
from inftybot.authentication.intents.base import AuthenticatedMixin
from inftybot.categories.models import Type
from inftybot.core.exceptions import ValidationError, APIResourceError
from inftybot.core.intents.base import BaseCommandIntent, BaseIntent, ObjectListKeyboardMixin
from inftybot.core.utils import render_model_errors, render_errors
from inftybot.topics.models import Topic
from inftybot.topics.utils import render_topic

_ = gettext.gettext
logger = logging.getLogger(__name__)

CHOOSE_TYPE_KEYBOARD = [
    [
        InlineKeyboardButton("Need", callback_data=inftybot.topics.constants.TOPIC_TYPE_NEED),
        InlineKeyboardButton("Goal", callback_data=inftybot.topics.constants.TOPIC_TYPE_GOAL),
        InlineKeyboardButton("Idea", callback_data=inftybot.topics.constants.TOPIC_TYPE_IDEA)
    ],
    [
        InlineKeyboardButton("Plan", callback_data=inftybot.topics.constants.TOPIC_TYPE_PLAN),
        InlineKeyboardButton("Step", callback_data=inftybot.topics.constants.TOPIC_TYPE_STEP),
        InlineKeyboardButton("Task", callback_data=inftybot.topics.constants.TOPIC_TYPE_TASK)
    ]
]


def prepare_categories(value):
    return list(filter(lambda v: v, (v.strip() for v in value.split(','))))


def send_confirm(bot, chat_id, topic):
    """Sends the topic preview"""
    bot.sendMessage(
        chat_id=chat_id,
        text=_("Well! That's your topic:"),
    )

    confirmation = render_topic(topic)

    bot.sendMessage(
        chat_id=chat_id,
        text=confirmation,
        parse_mode=ParseMode.MARKDOWN,
    )

    bot.sendMessage(
        chat_id=chat_id,
        text=_(
            "If it seems ok, please enter /done command, "
            "either enter /edit command"
        ),
    )


class BaseTopicIntent(BaseIntent):
    def reset_topic(self):
        try:
            del self.chat_data['topic']
        except KeyError:
            pass

    def set_topic(self, topic):
        if isinstance(topic, Topic):
            data = topic.to_native()
        else:
            data = topic

        self.chat_data['topic'] = data

    def get_topic(self):
        data = self.chat_data.get('topic')
        return Topic.from_native(data) if data else None


class TopicCategoryListMixin(ObjectListKeyboardMixin, BaseTopicIntent):
    model = Type

    def get_extra_params(self):
        return {'category': '1'}


class TopicDoneCommandIntent(AuthenticatedMixin, BaseTopicIntent, BaseCommandIntent):
    """Sends draft topic to the Infty API, resets topic creation context"""

    @classmethod
    def get_handler(cls):
        return CommandHandler("done", cls.as_callback(), pass_chat_data=True, pass_user_data=True)

    def validate(self):
        topic = self.get_topic()

        if topic is None:
            raise ValidationError("No topics to publish. Please, use /newtopic or /edit command.")

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

        message = "\n\n".join((_("Hmmm..."), message))

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
            raise APIResourceError('Failed to save the topic. Please, report it :/')
        else:
            self.reset_topic()

        self.update.message.reply_text(
            _("Done. Your topic: {}".format(rv.get('url')))
        )

        return inftybot.core.states.STATE_END
