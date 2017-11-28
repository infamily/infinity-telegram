# coding: utf-8
import gettext

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from telegram.ext import CommandHandler, ConversationHandler, CallbackQueryHandler

from inftybot.intents import constants, states
from inftybot.intents.base import BaseCommandIntent, BaseCallbackIntent, BaseConversationIntent, BaseMessageIntent, \
    CancelCommandIntent, AuthenticatedMixin
from inftybot.intents.basetopic import CHOOSE_TYPE_KEYBOARD, TopicDoneCommandIntent, BaseTopicIntent
from inftybot.intents.exceptions import IntentHandleException
from inftybot.intents.utils import render_topic

_ = gettext.gettext


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


class TopicEditCommandIntent(AuthenticatedMixin, BaseTopicIntent, BaseCommandIntent):
    """Enters topic edit context"""
    @classmethod
    def get_handler(cls):
        return CommandHandler("edit", cls.as_callback(), pass_chat_data=True)

    def get_keyboard(self):
        keyboard = [[], []]

        if self.topic and not self.topic.pk:
            keyboard[0].append(
                InlineKeyboardButton(
                    "Topic {}: {}".format(self.topic.type, self.topic.title),
                    callback_data=constants.TOPIC_EDIT_NEW,
                )
            )

        keyboard[0].append(
            InlineKeyboardButton("From DB", callback_data=constants.TOPIC_EDIT_EXISTED)
        )

        return keyboard

    def handle(self, *args, **kwargs):
        keyboard = self.get_keyboard()

        self.update.message.reply_text(
            _("What topic do you want to edit?"), reply_markup=InlineKeyboardMarkup(keyboard)
        )

        return states.TOPIC_STATE_EDIT_CHOOSE_TOPIC


class TopicChooseCallback(AuthenticatedMixin, BaseTopicIntent, BaseCallbackIntent):
    """Choose topic part for edit"""
    def get_keyboard(self):
        return [
            [
                InlineKeyboardButton("Type", callback_data=constants.TOPIC_PART_TYPE),
                InlineKeyboardButton("Title", callback_data=constants.TOPIC_PART_TITLE),
                InlineKeyboardButton("Body", callback_data=constants.TOPIC_PART_BODY)
            ],
        ]

    def handle(self, *args, **kwargs):
        keyboard = self.get_keyboard()

        choose = self.update.callback_query.data

        if choose == constants.TOPIC_EDIT_EXISTED:
            # todo load from db
            raise IntentHandleException("Not implemented yet")

        self.update.callback_query.message.reply_text(
            _("What topic part do you want to edit?"), reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return states.TOPIC_STATE_EDIT_CHOOSE_PART


class TopicEditIntent(AuthenticatedMixin, BaseTopicIntent, BaseCallbackIntent):
    """Intent (CallbackHandler) for start edit topic"""
    @classmethod
    def get_handler(cls):
        return CallbackQueryHandler(cls.as_callback(), pass_chat_data=True)

    def handle(self, *args, **kwargs):
        topic_part_mapping = {
            constants.TOPIC_PART_TYPE: states.TOPIC_STATE_TYPE,
            constants.TOPIC_PART_TITLE: states.TOPIC_STATE_TITLE,
            constants.TOPIC_PART_BODY: states.TOPIC_STATE_BODY,
        }

        new_state = topic_part_mapping.get(self.update.callback_query.data)
        reply_markup = None

        if new_state is states.TOPIC_STATE_TYPE:
            message = _('Please, choose new type')
            keyboard = CHOOSE_TYPE_KEYBOARD
            reply_markup = InlineKeyboardMarkup(keyboard)
        elif new_state is states.TOPIC_STATE_TITLE:
            message = _('Please, enter new title')
        elif new_state is states.TOPIC_STATE_BODY:
            message = _('Please, enter new body')
        else:
            message = _('Unknown state. Please report it.')

        self.bot.sendMessage(
            chat_id=self.update.callback_query.message.chat_id,
            text=message,
            reply_markup=reply_markup
        )

        return new_state

    def handle_error(self, error):
        self.bot.sendMessage(
            chat_id=self.update.callback_query.message.chat_id,
            text=error.message,
        )


class EditTypeIntent(AuthenticatedMixin, BaseTopicIntent, BaseCallbackIntent):
    """Edit topic type"""
    def handle(self, *args, **kwargs):
        topic = self.chat_data['topic']
        topic.type = int(self.update.callback_query.data)

        self.chat_data['topic'] = topic

        send_confirm(
            self.bot,
            self.update.callback_query.message.chat_id,
            topic
        )

        return states.TOPIC_STATE_EDIT


class EditTitleIntent(AuthenticatedMixin, BaseTopicIntent, BaseMessageIntent):
    """Edit topic title"""
    def handle(self, *args, **kwargs):
        topic = self.chat_data['topic']
        topic.title = self.update.message.text
        self.chat_data['topic'] = topic

        send_confirm(
            self.bot,
            self.update.message.chat_id,
            topic
        )

        return states.TOPIC_STATE_EDIT


class EditBodyIntent(AuthenticatedMixin, BaseTopicIntent, BaseMessageIntent):
    """Edit topic body"""
    def handle(self, *args, **kwargs):
        topic = self.chat_data['topic']
        topic.body = self.update.message.text
        self.chat_data['topic'] = topic

        send_confirm(
            self.bot,
            self.update.message.chat_id,
            topic
        )

        return states.TOPIC_STATE_EDIT


class TopicConversationIntent(BaseConversationIntent):
    """Edit conversation"""
    @classmethod
    def get_handler(cls):
        return ConversationHandler(
            entry_points=[TopicEditCommandIntent.get_handler()],
            states={
                states.TOPIC_STATE_EDIT: [TopicEditCommandIntent.get_handler()],
                states.TOPIC_STATE_EDIT_CHOOSE_TOPIC: [TopicChooseCallback.get_handler()],
                states.TOPIC_STATE_EDIT_CHOOSE_PART: [TopicEditIntent.get_handler()],
                states.TOPIC_STATE_TYPE: [EditTypeIntent.get_handler()],
                states.TOPIC_STATE_TITLE: [EditTitleIntent.get_handler()],
                states.TOPIC_STATE_BODY: [EditBodyIntent.get_handler()],
            },
            fallbacks=[
                TopicDoneCommandIntent.get_handler(),
                CancelCommandIntent.get_handler(),
            ],
        )
