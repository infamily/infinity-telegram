# coding: utf-8
import logging

from django.db import models
from django.forms import model_to_dict
from django.template import loader
from django.utils.translation import gettext
from slumber.exceptions import HttpClientError, HttpServerError
from telegram import InlineKeyboardButton, ParseMode
from telegram.ext import CommandHandler

import inftybot.core.states
import inftybot.topics.constants
from inftybot.authentication.intents.base import AuthenticatedMixin
from inftybot.categories.models import Type
from inftybot.core.exceptions import ValidationError, APIResourceError
from inftybot.core.intents.base import BaseCommandIntent, BaseIntent, ObjectListKeyboardMixin
from inftybot.core.utils import render_form_errors, render_errors
from inftybot.topics.serializers import TopicSerializer

_ = gettext
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

    confirmation = loader.render_to_string('topics/topic.md', topic)

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
            del self.current_chat.chatdata.data['topic']
            self.current_chat.chatdata.save()
        except KeyError:
            pass

    def set_topic(self, data):
        if isinstance(data, models.Model):
            data = model_to_dict(data)
        self.current_chat.chatdata.data['topic'] = data
        self.current_chat.chatdata.save()

    def get_topic(self):
        return self.current_chat.chatdata.data.get('topic', None)

    def fetch_topic(self, pk):
        """
        Loads topic from API
        """
        response = self.api.client.topics(pk).get()
        return response

    def get_topic_serializer(self, data=None):
        return TopicSerializer(data=data)


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
        stored_data = self.get_topic()
        if not stored_data:
            raise ValidationError("No topics to publish. Please, use /newtopic or /edit command.")

        serializer = self.get_topic_serializer(stored_data)
        if not serializer.is_valid():
            errors = render_form_errors(serializer)
            raise ValidationError(errors)

    def handle_error(self, error):
        if isinstance(error.message, list):
            message = render_errors(error.message)
        else:
            message = error.message

        self.update.message.reply_text(_("Please, check this errors:"))
        self.update.message.reply_text(message)

    def handle(self, *args, **kwargs):
        stored_data = self.get_topic()

        if not stored_data or not stored_data.get('id'):
            method = self.api.client.topics.post
        else:
            method = self.api.client.topics(int(stored_data['id'])).put

        try:
            rv = method(data=stored_data)
        except (HttpClientError, HttpServerError) as e:
            # intercept 4xx and 5xx both
            raise APIResourceError('Failed to save the topic. Please, report it :/')
        else:
            self.reset_topic()

        self.update.message.reply_text(
            _("Done. Your topic: {}".format(rv.get('url')))
        )

        return inftybot.core.states.STATE_END
