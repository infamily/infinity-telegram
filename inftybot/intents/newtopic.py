# coding: utf-8
import gettext

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from telegram.ext import CommandHandler, ConversationHandler

from inftybot.intents import constants, states
from inftybot.intents.base import BaseCommandIntent, BaseCallbackIntent, BaseConversationIntent, BaseMessageIntent, \
    CancelCommandIntent, BaseIntent
from schematics.exceptions import DataError
from inftybot.intents.exceptions import ValidationError
from inftybot.intents.utils import render_topic, render_model_errors
from inftybot.models import Topic

_ = gettext.gettext


class TopicCreateCommandIntent(BaseCommandIntent):
    """Enters topic creation context"""
    @classmethod
    def get_handler(cls):
        return CommandHandler("newtopic", cls.as_callback(), pass_chat_data=True)

    def get_keyboard(self):
        return [
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

    def handle(self, *args, **kwargs):
        keyboard = self.get_keyboard()
        self.update.message.reply_text(
            _("Please, choose:"), reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return states.TOPIC_STATE_TYPE


class NewTopicMixin(BaseIntent):
    """Mixin adds new topic model to the chat data if necessary"""
    def before_validate(self):
        self.chat_data.setdefault('topic', Topic())
        super(NewTopicMixin, self).before_handle()


class TopicDoneCommandIntent(NewTopicMixin, BaseCommandIntent):
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

        rv = self.api.client.topics.post(data=topic.to_native())

        # todo
        # handle creation
        # handle editing
        # handle remove ?
        self.update.message.reply_text(
            _("Done")
        )
        return states.STATE_END


class TopicTypeIntent(NewTopicMixin, BaseCallbackIntent):
    def handle(self, *args, **kwargs):
        topic = self.chat_data['topic']
        topic.type = int(self.update.callback_query.data)
        self.chat_data['topic'] = topic
        self.bot.sendMessage(
            chat_id=self.update.callback_query.message.chat_id,
            text=_("Well! Please, tell me the topic title"),
        )
        return states.TOPIC_STATE_TITLE


class TopicTitleIntent(NewTopicMixin, BaseMessageIntent):
    def handle(self, *args, **kwargs):
        topic = self.chat_data['topic']
        topic.title = self.update.message.text
        self.chat_data['topic'] = topic
        self.update.message.reply_text(
            _("Ok! Please, input the topic body")
        )
        return states.TOPIC_STATE_BODY


class TopicBodyIntent(NewTopicMixin, BaseMessageIntent):
    def handle(self, *args, **kwargs):
        topic = self.chat_data['topic']
        topic.body = self.update.message.text
        self.chat_data['topic'] = topic

        self.update.message.reply_text(
            _("Good! Please, check:")
        )

        confirmation = render_topic(topic)
        self.update.message.reply_text(
            confirmation,
            parse_mode=ParseMode.MARKDOWN,
        )

        self.update.message.reply_text(
            _("If it seems ok, please enter /done command, "
              "either enter /edit command")
        )


class TopicConversationIntent(BaseConversationIntent):
    @classmethod
    def get_handler(cls):
        return ConversationHandler(
            entry_points=[TopicCreateCommandIntent.get_handler()],
            states={
                states.TOPIC_STATE_TYPE: [TopicTypeIntent.get_handler()],
                states.TOPIC_STATE_TITLE: [TopicTitleIntent.get_handler()],
                states.TOPIC_STATE_BODY: [TopicBodyIntent.get_handler()],
            },
            fallbacks=[
                TopicDoneCommandIntent.get_handler(),
                CancelCommandIntent.get_handler(),
            ],
        )
