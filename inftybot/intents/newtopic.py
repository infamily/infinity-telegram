# coding: utf-8
import gettext

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, ConversationHandler

from inftybot.intents import constants, states
from inftybot.intents.base import BaseCommandIntent, BaseCallbackIntent, BaseConversationIntent, BaseMessageIntent, \
    CancelCommandIntent
from inftybot.intents.exceptions import ValidationError

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


class TopicDoneCommandIntent(BaseCommandIntent):
    """Sends created topic to the Infty API, resets topic creation context"""
    @classmethod
    def get_handler(cls):
        return CommandHandler("done", cls.as_callback(), pass_chat_data=True)

    def handle(self, *args, **kwargs):
        # todo
        # handle creation
        # handle editing
        # handle remove ?
        self.update.message.reply_text(
            _("Done")
        )
        return states.STATE_END


class TopicTypeIntent(BaseCallbackIntent):
    def handle(self, *args, **kwargs):
        pass


class TopicTitleIntent(BaseMessageIntent):
    def handle(self, *args, **kwargs):
        pass


class TopicBodyIntent(BaseMessageIntent):
    def handle(self, *args, **kwargs):
        pass


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
