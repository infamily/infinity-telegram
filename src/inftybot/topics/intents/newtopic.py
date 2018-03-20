# coding: utf-8
from django.utils.translation import gettext as _
from telegram import InlineKeyboardMarkup
from telegram.ext import CommandHandler

import inftybot.core.states
import inftybot.topics.states
from contrib.telegram.ext import ConversationHandler
from inftybot.authentication.intents.base import AuthenticatedMixin
from inftybot.core.intents.base import BaseCommandIntent, BaseConversationIntent
from inftybot.core.intents.cancel import CancelCommandIntent
from inftybot.topics.intents.base import CHOOSE_TYPE_KEYBOARD, TopicDoneCommandIntent, BaseTopicIntent, send_confirm, \
    BaseInputTypeIntent, BaseInputCategoryIntent, BaseInputTitleIntent, BaseInputBodyIntent
from inftybot.topics.models import Topic


class TopicCreateCommandIntent(AuthenticatedMixin, BaseTopicIntent, BaseCommandIntent):
    """Enters topic creation context"""

    @classmethod
    def get_handler(cls):
        return CommandHandler("newtopic", cls.as_callback(), pass_chat_data=True, pass_user_data=True)

    def handle(self, *args, **kwargs):
        self.reset_topic()
        self.set_topic(Topic())

        keyboard = CHOOSE_TYPE_KEYBOARD
        self.update.message.reply_text(
            _("Please, choose type:"), reply_markup=InlineKeyboardMarkup(keyboard)
        )

        return inftybot.topics.states.TOPIC_STATE_TYPE


class InputTypeIntent(BaseInputTypeIntent):
    next_state = inftybot.topics.states.TOPIC_STATE_CATEGORY

    def handle(self, *args, **kwargs):
        next_state = super(InputTypeIntent, self).handle(*args, **kwargs)
        self.bot.sendMessage(
            chat_id=self.update.callback_query.message.chat_id,
            text=_(
                "Please, enter some categories (comma-separated). "
                "Use /listcategories to check the available ones"
            ),
        )
        return next_state


class InputCategoryIntent(BaseInputCategoryIntent):
    next_state = inftybot.topics.states.TOPIC_STATE_TITLE

    def handle(self, *args, **kwargs):
        next_state = super(InputCategoryIntent, self).handle(*args, **kwargs)
        self.bot.sendMessage(
            chat_id=self.update.message.chat_id,
            text=_("Ok! Please, input the topic title"),
        )
        return next_state


class InputTitleIntent(BaseInputTitleIntent):
    next_state = inftybot.topics.states.TOPIC_STATE_BODY

    def handle(self, *args, **kwargs):
        next_state = super(InputTitleIntent, self).handle(*args, **kwargs)
        self.update.message.reply_text(
            _("Ok! Please, input the topic body")
        )
        return next_state


class InputBodyIntent(BaseInputBodyIntent):
    next_state = inftybot.core.states.STATE_END

    def handle(self, *args, **kwargs):
        next_state = super(InputBodyIntent, self).handle(*args, **kwargs)
        topic = self.get_topic()
        send_confirm(
            self.bot,
            self.update.message.chat_id,
            topic
        )
        return next_state


class TopicConversationIntent(BaseConversationIntent):
    @classmethod
    def get_handler(cls):
        return ConversationHandler(
            entry_points=[TopicCreateCommandIntent.get_handler()],
            states={
                inftybot.topics.states.TOPIC_STATE_TYPE: [InputTypeIntent.get_handler()],
                inftybot.topics.states.TOPIC_STATE_TITLE: [InputTitleIntent.get_handler()],
                inftybot.topics.states.TOPIC_STATE_CATEGORY: [InputCategoryIntent.get_handler()],
                inftybot.topics.states.TOPIC_STATE_BODY: [InputBodyIntent.get_handler()],
            },
            fallbacks=[
                TopicDoneCommandIntent.get_handler(),
                CancelCommandIntent.get_handler(),
            ],
        )
