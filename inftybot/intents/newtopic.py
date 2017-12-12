# coding: utf-8
import gettext

from telegram import InlineKeyboardMarkup, ParseMode
from telegram.ext import CommandHandler, ConversationHandler

from inftybot.intents import states
from inftybot.intents.base import BaseCommandIntent, BaseCallbackIntent, BaseConversationIntent, BaseMessageIntent, \
    CancelCommandIntent, BaseIntent, AuthenticatedMixin
from inftybot.intents.basetopic import CHOOSE_TYPE_KEYBOARD, TopicDoneCommandIntent
from inftybot.intents.utils import render_topic
from inftybot.models import Topic

_ = gettext.gettext


class TopicCreateCommandIntent(AuthenticatedMixin, BaseCommandIntent):
    """Enters topic creation context"""
    @classmethod
    def get_handler(cls):
        return CommandHandler("newtopic", cls.as_callback(), pass_chat_data=True, pass_user_data=True)

    def handle(self, *args, **kwargs):
        keyboard = CHOOSE_TYPE_KEYBOARD
        self.update.message.reply_text(
            _("Please, choose:"), reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return states.TOPIC_STATE_TYPE


class NewTopicIntent(AuthenticatedMixin, BaseIntent):
    """Mixin adds new topic model to the chat data if necessary"""
    def before_validate(self):
        super(NewTopicIntent, self).before_validate()
        self.chat_data.setdefault('topic', Topic())


class TopicTypeIntent(NewTopicIntent, BaseCallbackIntent):
    def handle(self, *args, **kwargs):
        topic = self.chat_data['topic']
        topic.type = int(self.update.callback_query.data)
        self.chat_data['topic'] = topic
        self.bot.sendMessage(
            chat_id=self.update.callback_query.message.chat_id,
            text=_("Well! Please, tell me the topic title"),
        )
        return states.TOPIC_STATE_TITLE


class TopicTitleIntent(NewTopicIntent, BaseMessageIntent):
    def handle(self, *args, **kwargs):
        topic = self.chat_data['topic']
        topic.title = self.update.message.text
        self.chat_data['topic'] = topic
        self.update.message.reply_text(
            _("Ok! Please, input the topic body")
        )
        return states.TOPIC_STATE_BODY


class TopicBodyIntent(NewTopicIntent, BaseMessageIntent):
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
