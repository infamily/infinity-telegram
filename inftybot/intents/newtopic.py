# coding: utf-8
import gettext

from telegram import InlineKeyboardMarkup
from telegram.ext import CommandHandler, ConversationHandler

from inftybot.intents import states
from inftybot.intents.base import BaseCommandIntent, BaseConversationIntent, CancelCommandIntent, AuthenticatedMixin, \
    BaseCallbackIntent, BaseMessageIntent
from inftybot.intents.basetopic import CHOOSE_TYPE_KEYBOARD, TopicDoneCommandIntent, BaseTopicIntent, send_confirm
from inftybot.models import Topic

_ = gettext.gettext


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

        return states.TOPIC_STATE_TYPE


class InputTypeIntent(BaseTopicIntent, BaseCallbackIntent):
    def handle(self, *args, **kwargs):
        topic = self.get_topic()
        topic.type = int(self.update.callback_query.data)
        self.set_topic(topic)
        self.bot.sendMessage(
            chat_id=self.update.callback_query.message.chat_id,
            text=_("Please, enter some categories (comma-separated)"),
        )
        return states.TOPIC_STATE_CATEGORY


class InputCategoryIntent(BaseTopicIntent, BaseMessageIntent):
    def handle(self, *args, **kwargs):
        topic = self.get_topic()
        topic.categories_str = self.update.message.text
        self.set_topic(topic)
        self.bot.sendMessage(
            chat_id=self.update.message.chat_id,
            text=_("Ok! Please, input the topic title"),
        )
        return states.TOPIC_STATE_TITLE


class InputTitleIntent(BaseTopicIntent, BaseMessageIntent):
    def handle(self, *args, **kwargs):
        topic = self.get_topic()
        topic.title = self.update.message.text
        self.set_topic(topic)
        self.update.message.reply_text(
            _("Ok! Please, input the topic body")
        )
        return states.TOPIC_STATE_BODY


class InputBodyIntent(BaseTopicIntent, BaseMessageIntent):
    def handle(self, *args, **kwargs):
        topic = self.get_topic()
        topic.body = self.update.message.text
        self.set_topic(topic)

        send_confirm(
            self.bot,
            self.update.message.chat_id,
            topic
        )

        return states.STATE_END


class TopicConversationIntent(BaseConversationIntent):
    @classmethod
    def get_handler(cls):
        return ConversationHandler(
            entry_points=[TopicCreateCommandIntent.get_handler()],
            states={
                states.TOPIC_STATE_TYPE: [InputTypeIntent.get_handler()],
                states.TOPIC_STATE_TITLE: [InputTitleIntent.get_handler()],
                states.TOPIC_STATE_CATEGORY: [InputCategoryIntent.get_handler()],
                states.TOPIC_STATE_BODY: [InputBodyIntent.get_handler()],
            },
            fallbacks=[
                TopicDoneCommandIntent.get_handler(),
                CancelCommandIntent.get_handler(),
            ],
        )
