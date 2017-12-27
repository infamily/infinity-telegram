# coding: utf-8
import gettext

from slumber.exceptions import HttpClientError
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from telegram.ext import CommandHandler, ConversationHandler, CallbackQueryHandler

from inftybot.intents import constants, states
from inftybot.intents.base import BaseCommandIntent, BaseCallbackIntent, BaseConversationIntent, BaseMessageIntent, \
    CancelCommandIntent, AuthenticatedMixin
from inftybot.intents.basetopic import CHOOSE_TYPE_KEYBOARD, TopicDoneCommandIntent, BaseTopicIntent
from inftybot.intents.exceptions import IntentHandleException
from inftybot.intents.utils import render_topic
from inftybot.models import Topic
from inftybot.utils import build_menu

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


def format_topic(topic):
    topic_str = "{}: {}".format(
        constants.TOPIC_TYPE_CHOICES[topic.type], topic.title or '<no title>'
    )
    if not topic.id:
        topic_str = "{} (draft)".format(topic_str)

    return topic_str


class TopicRetrieveMixin(BaseTopicIntent):
    def fetch_topic(self, pk):
        """
        Loads topic from API
        """
        response = self.api.client.topics(pk).get()
        return Topic.from_native(response)


class TopicListRetrieveMixin(BaseTopicIntent):
    """
    todo: bad design, needs refactor: split it to Mixin & ApiResponsePaginator, maybe
    """

    def __init__(self, **kwargs):
        super(TopicListRetrieveMixin, self).__init__(**kwargs)
        self.topics = []
        self.next_page_url = None
        self.prev_page_url = None

    @property
    def has_next_page(self):
        return bool(self.next_page_url)

    @property
    def has_prev_page(self):
        return bool(self.prev_page_url)

    def get_keyboard(self):
        if not self.topics:
            self.topics = self.fetch_topics()

        current_topic = self.get_topic()
        current_topic_id = current_topic.id if current_topic else None

        buttons, header_buttons, footer_buttons = [], [], []

        for topic in filter(lambda t: t.id != current_topic_id or None, self.topics):
            buttons.append(
                InlineKeyboardButton(
                    format_topic(topic),
                    callback_data=topic.id,
                )
            )

        if current_topic:
            header_buttons.append(
                InlineKeyboardButton(
                    _("(Current) {}").format(
                        format_topic(current_topic)
                    ), callback_data=constants.CURRENT_TOPIC,
                )
            )

        if self.has_prev_page:
            footer_buttons.append(
                InlineKeyboardButton(
                    "<<", callback_data=constants.PREV_PAGE,
                )
            )

        if self.has_next_page:
            footer_buttons.append(
                InlineKeyboardButton(
                    ">>", callback_data=constants.NEXT_PAGE,
                )
            )

        return build_menu(
            buttons, 2, header_buttons=header_buttons, footer_buttons=footer_buttons
        )

    def fetch_topics(self):
        """
        Loads topics from API
        Returns List[Topic]
        """
        params = {'owner': 'me', 'page': self.current_page}

        try:
            response = self.api.client.topics.get(**params)
        except HttpClientError as e:
            return []

        if response['next']:
            self.next_page_url = response['next']
        else:
            self.next_page_url = None

        if response['previous']:
            self.prev_page_url = response['previous']
        else:
            self.prev_page_url = None

        return [Topic.from_native(data) for data in response['results']]

    @property
    def current_page(self):
        return int(self.chat_data.get('current_page', 1))

    @current_page.setter
    def current_page(self, value):
        self.chat_data['current_page'] = int(value) or 1

    def get_next_page(self):
        return self.next_page_url.split('page')[-1] if self.next_page_url else None

    def get_prev_page(self):
        return self.prev_page_url.split('page')[-1] if self.prev_page_url else None


class TopicEditCommandIntent(AuthenticatedMixin, TopicListRetrieveMixin, BaseTopicIntent, BaseCommandIntent):
    """Enters topic edit context"""

    @classmethod
    def get_handler(cls):
        return CommandHandler("edit", cls.as_callback(), pass_chat_data=True, pass_user_data=True)

    def handle(self, *args, **kwargs):
        self.current_page = 1
        message_text = _("Please, choose the topic for editing")
        keyboard = self.get_keyboard()

        self.bot.send_message(
            chat_id=self.update.effective_chat.id,
            text=message_text,
            reply_markup=InlineKeyboardMarkup(keyboard),
        )

        return states.TOPIC_STATE_EDIT_CHOOSE_TOPIC


class TopicChooseCallback(AuthenticatedMixin, TopicListRetrieveMixin, TopicRetrieveMixin, BaseTopicIntent, BaseCallbackIntent):
    """Choose topic to edit"""

    def handle_pagination(self):
        choose = self.get_choose()

        if choose == constants.NEXT_PAGE:
            # we've choosed next page
            self.current_page = self.current_page + 1
        elif choose == constants.PREV_PAGE:
            # we've choosed prev page
            self.current_page = self.current_page - 1

        keyboard = self.get_keyboard()
        message_text = _("Page {}".format(self.current_page))

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

        if choose in (constants.NEXT_PAGE, constants.PREV_PAGE):
            return self.handle_pagination()
        else:
            return self.handle_choose_topic()


class TopicPartChooseCallback(AuthenticatedMixin, TopicRetrieveMixin, BaseTopicIntent, BaseCallbackIntent):
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
        return states.TOPIC_STATE_EDIT_INPUT


class TopicEditIntent(AuthenticatedMixin, BaseTopicIntent, BaseCallbackIntent):
    """Intent (CallbackHandler) for start edit topic"""

    @classmethod
    def get_handler(cls):
        return CallbackQueryHandler(cls.as_callback(), pass_chat_data=True, pass_user_data=True)

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
        topic = self.get_topic()
        topic.type = int(self.update.callback_query.data)
        self.set_topic(topic)

        send_confirm(
            self.bot,
            self.update.callback_query.message.chat_id,
            topic
        )

        return states.TOPIC_STATE_EDIT


class EditTitleIntent(AuthenticatedMixin, BaseTopicIntent, BaseMessageIntent):
    """Edit topic title"""

    def handle(self, *args, **kwargs):
        topic = self.get_topic()
        topic.title = self.update.message.text
        self.set_topic(topic)

        send_confirm(
            self.bot,
            self.update.message.chat_id,
            topic
        )

        return states.TOPIC_STATE_EDIT


class EditBodyIntent(AuthenticatedMixin, BaseTopicIntent, BaseMessageIntent):
    """Edit topic body"""

    def handle(self, *args, **kwargs):
        topic = self.get_topic()
        topic.body = self.update.message.text
        self.set_topic(topic)

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
                states.TOPIC_STATE_EDIT_CHOOSE_PART: [TopicPartChooseCallback.get_handler()],
                states.TOPIC_STATE_EDIT_INPUT: [TopicEditIntent.get_handler()],
                states.TOPIC_STATE_TYPE: [EditTypeIntent.get_handler()],
                states.TOPIC_STATE_TITLE: [EditTitleIntent.get_handler()],
                states.TOPIC_STATE_BODY: [EditBodyIntent.get_handler()],
            },
            fallbacks=[
                TopicDoneCommandIntent.get_handler(),
                CancelCommandIntent.get_handler(),
            ],
        )
