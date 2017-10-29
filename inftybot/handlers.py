# coding: utf-8
from uuid import uuid4
import telegram

from . import constants


def start_command_handler(bot, update):
    update.message.reply_text("Hey, start command!")


def inline_query_handler(bot, update):
    if update.inline_query.query not in constants.TOPIC_TYPES_LIST:
        results = []
    else:
        results = [
            telegram.InlineQueryResultArticle(
                id=uuid4(),
                title="Test",
                url="http://google.com",
                input_message_content=telegram.InputTextMessageContent(
                    "Test result text",
                    parse_mode=telegram.ParseMode.MARKDOWN,
                    disable_web_page_preview=True
                )
            )
        ]

    update.inline_query.answer(results)


def common_message_handler(bot, update):
    update.message.reply_text("Hey, message!")
