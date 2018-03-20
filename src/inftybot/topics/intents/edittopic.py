# coding: utf-8
from django.utils.translation import gettext_lazy as _
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from telegram.ext import CommandHandler, ConversationHandler, CallbackQueryHandler

import inftybot.core.constants
import inftybot.topics.constants
import inftybot.topics.states
from inftybot.authentication.intents.base import AuthenticatedMixin
from inftybot.core.exceptions import IntentHandleException
from inftybot.core.intents.base import BaseCommandIntent, BaseCallbackIntent, BaseConversationIntent, \
    BaseMessageIntent, ObjectListKeyboardMixin
from inftybot.core.intents.cancel import CancelCommandIntent
from inftybot.topics.intents.base import TopicDoneCommandIntent, BaseTopicIntent, CHOOSE_TYPE_KEYBOARD, send_confirm, \
    TopicCategoryListMixin, prepare_categories
from inftybot.topics.models import Topic
from inftybot.topics.serializers import TopicSerializer
from inftybot.topics.utils import render_topic


class TopicListKeyboardMixin(ObjectListKeyboardMixin, BaseTopicIntent):
    """Mixin for provide current user owned topic list in the keyboard"""
    model = Topic
    serializer = TopicSerializer

    def get_extra_params(self):
        return {'owner': 'me'}

    def filter_list(self, lst):
        """Filters out current (choosed) topic"""
        current_object = self.get_topic()
        current_object_id = current_object['id'] if current_object else None
        return filter(lambda t: t.id != current_object_id or None, lst)


class TopicEditCommandIntent(AuthenticatedMixin, TopicListKeyboardMixin, BaseCommandIntent):
    """Enters topic edit context"""

    @classmethod
    def get_handler(cls):
        return CommandHandler("edit", cls.as_callback(), pass_chat_data=True, pass_user_data=True)

    def handle(self, *args, **kwargs):
        self.set_current_page(1)

        message_text = _("Please, choose the topic for editing")
        keyboard = self.get_keyboard()

        current_object = self.get_topic()
        if current_object:
            keyboard.insert(0, [InlineKeyboardButton(
                _("(Current) {}").format(
                    self.format_object(current_object)
                ), callback_data=inftybot.core.constants.CURRENT,
            )])

        self.bot.send_message(
            chat_id=self.update.effective_chat.id,
            text=str(message_text),
            reply_markup=InlineKeyboardMarkup(keyboard),
        )

        return inftybot.topics.states.TOPIC_STATE_EDIT_CHOOSE_TOPIC


class TopicChooseCallback(AuthenticatedMixin, TopicListKeyboardMixin, BaseTopicIntent,
                          BaseCallbackIntent):
    """Choose topic to edit"""

    def handle_pagination(self):
        choose = self.get_choose()

        current_page = self.get_current_page()

        if choose == inftybot.core.constants.NEXT_PAGE:
            # we've choosed next page
            current_page = current_page + 1
        elif choose == inftybot.core.constants.PREV_PAGE:
            # we've choosed prev page
            current_page = current_page - 1

        self.set_current_page(current_page)

        keyboard = self.get_keyboard()
        message_text = _("Page {}".format(current_page))

        self.bot.send_message(
            chat_id=self.update.effective_chat.id,
            text=message_text,
            reply_markup=InlineKeyboardMarkup(keyboard),
        )

        return None

    def handle_choose_topic(self):
        choose = self.get_choose()

        try:
            pk = int(choose)
        except ValueError:
            pass
        else:
            topic_from_db = self.fetch_topic(pk)
            self.set_topic(topic_from_db)

        next_intent = TopicPartChooseCallback.create_from_intent(self)
        return next_intent()

    def handle(self, *args, **kwargs):
        choose = self.get_choose()

        if choose in (inftybot.core.constants.NEXT_PAGE, inftybot.core.constants.PREV_PAGE):
            return self.handle_pagination()
        else:
            return self.handle_choose_topic()


class TopicPartChooseCallback(AuthenticatedMixin, BaseTopicIntent, BaseCallbackIntent):
    """Choose topic part for edit"""

    def get_keyboard(self):
        return [
            [InlineKeyboardButton(label, callback_data=value) for value, label in
             inftybot.topics.constants.TOPIC_PART_CHOIES],
        ]

    def handle(self, *args, **kwargs):
        keyboard = self.get_keyboard()
        topic = self.get_topic()

        if not topic:
            raise IntentHandleException("Can not resolve topic. Please, report it")
        else:
            self.update.callback_query.message.reply_text(
                render_topic(topic),
                parse_mode=ParseMode.MARKDOWN,
            )

        self.update.callback_query.message.reply_text(
            _("What topic part do you want to edit?"),
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return inftybot.topics.states.TOPIC_STATE_EDIT_INPUT


class TopicEditIntent(AuthenticatedMixin, TopicCategoryListMixin, BaseTopicIntent, BaseCallbackIntent):
    """Intent (CallbackHandler) for start edit topic"""

    @classmethod
    def get_handler(cls):
        return CallbackQueryHandler(cls.as_callback(), pass_chat_data=True, pass_user_data=True)

    def get_extra_params(self):
        return {'lang': 'en'}

    def handle(self, *args, **kwargs):
        topic_part_mapping = {
            inftybot.topics.constants.TOPIC_PART_TYPE: inftybot.topics.states.TOPIC_STATE_TYPE,
            inftybot.topics.constants.TOPIC_PART_TITLE: inftybot.topics.states.TOPIC_STATE_TITLE,
            inftybot.topics.constants.TOPIC_PART_BODY: inftybot.topics.states.TOPIC_STATE_BODY,
            inftybot.topics.constants.TOPIC_PART_CATEGORY: inftybot.topics.states.TOPIC_STATE_CATEGORY,
        }

        new_state = topic_part_mapping.get(self.update.callback_query.data)
        reply_markup = None

        if new_state is inftybot.topics.states.TOPIC_STATE_TYPE:
            message = _('Please, choose topic type')
            keyboard = CHOOSE_TYPE_KEYBOARD
            reply_markup = InlineKeyboardMarkup(keyboard)
        elif new_state is inftybot.topics.states.TOPIC_STATE_CATEGORY:
            message = _(
                'Please, enter some categories (comma-separated). '
                'Use /listcategories to check the available ones'
            )
        elif new_state is inftybot.topics.states.TOPIC_STATE_TITLE:
            message = _('Please, enter topic title')
        elif new_state is inftybot.topics.states.TOPIC_STATE_BODY:
            message = _('Please, enter topic body')
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


class InputCategoryIntent(AuthenticatedMixin, BaseTopicIntent, BaseMessageIntent):
    """Edit topic category"""

    def handle(self, *args, **kwargs):
        topic = self.get_topic()
        topic['categories_names'] = prepare_categories(self.update.message.text)
        self.set_topic(topic)

        send_confirm(
            self.bot,
            self.update.message.chat_id,
            topic
        )

        return inftybot.topics.states.TOPIC_STATE_EDIT


class InputTypeIntent(AuthenticatedMixin, BaseTopicIntent, BaseCallbackIntent):
    """Edit topic type"""

    def handle(self, *args, **kwargs):
        topic = self.get_topic()
        topic['type'] = int(self.update.callback_query.data)
        self.set_topic(topic)

        send_confirm(
            self.bot,
            self.update.callback_query.message.chat_id,
            topic
        )

        return inftybot.topics.states.TOPIC_STATE_EDIT


class InputTitleIntent(AuthenticatedMixin, BaseTopicIntent, BaseMessageIntent):
    """Edit topic title"""

    def handle(self, *args, **kwargs):
        topic = self.get_topic()
        topic['title'] = self.update.message.text
        self.set_topic(topic)

        send_confirm(
            self.bot,
            self.update.message.chat_id,
            topic
        )

        return inftybot.topics.states.TOPIC_STATE_EDIT


class InputBodyIntent(AuthenticatedMixin, BaseTopicIntent, BaseMessageIntent):
    """Edit topic body"""

    def handle(self, *args, **kwargs):
        topic = self.get_topic()
        topic['body'] = self.update.message.text
        self.set_topic(topic)

        send_confirm(
            self.bot,
            self.update.message.chat_id,
            topic
        )

        return inftybot.topics.states.TOPIC_STATE_EDIT


class TopicConversationIntent(BaseConversationIntent):
    """Edit conversation"""

    @classmethod
    def get_handler(cls):
        return ConversationHandler(
            entry_points=[TopicEditCommandIntent.get_handler()],
            states={
                inftybot.topics.states.TOPIC_STATE_EDIT: [TopicEditCommandIntent.get_handler()],
                inftybot.topics.states.TOPIC_STATE_EDIT_CHOOSE_TOPIC: [TopicChooseCallback.get_handler()],
                inftybot.topics.states.TOPIC_STATE_EDIT_CHOOSE_PART: [TopicPartChooseCallback.get_handler()],
                inftybot.topics.states.TOPIC_STATE_EDIT_INPUT: [TopicEditIntent.get_handler()],
                inftybot.topics.states.TOPIC_STATE_CATEGORY: [InputCategoryIntent.get_handler()],
                inftybot.topics.states.TOPIC_STATE_TYPE: [InputTypeIntent.get_handler()],
                inftybot.topics.states.TOPIC_STATE_TITLE: [InputTitleIntent.get_handler()],
                inftybot.topics.states.TOPIC_STATE_BODY: [InputBodyIntent.get_handler()],
            },
            fallbacks=[
                TopicDoneCommandIntent.get_handler(),
                CancelCommandIntent.get_handler(),
            ],
        )
