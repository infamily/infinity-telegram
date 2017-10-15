#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import uuid
import logging
import requests
import urllib.parse

from telegram import (
    ParseMode,
    InlineQueryResultArticle,
    InputTextMessageContent,
)
from telegram.ext import (
    Updater,
    InlineQueryHandler,
    CommandHandler
)


class Settings:
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    TELEGRAM_SEARCH_MIN_CHAR_COUNT = 3
    TELEGRAM_SEARCH_RESULTS_LIMIT = 50
    SEARCH_PREVIEW_LENGTH = 200
    LOGGING_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    WEFINDX_API_BASE = os.getenv('WFX_API_SERVER', 'https://test.wfx.io/')
    WEFINDX_API_VERSION = 'v1'

settings = Settings()

logging.basicConfig(
    format = settings.LOGGING_FORMAT,
    level = logging.INFO
)
logger = logging.getLogger(__name__)


class Utils:

    def collapse_newlines(self, text):
        return text.replace('\n', ' ')


utils = Utils()


class Agent:

    def __init__(self, BOT_TOKEN):
        self.endpoints = requests.get(settings.WEFINDX_API_BASE).json()['api'][settings.WEFINDX_API_VERSION]
        self.updater = Updater(BOT_TOKEN)
        self.router = self.updater.dispatcher

    def run(self):
        self.updater.start_polling()
        self.updater.idle()

    def search_topics(self, query):

        response = requests.get(
            urllib.parse.urljoin(settings.WEFINDX_API_BASE, self.endpoints['topics']),
                params={'format': 'json', 'search': query}
            )

        return response.json()

    def start(self, bot, update):
        bot_username = bot.getMe().username
        update.message.reply_text(
            'Just type @{} to start searching topics. Type at least 3 letters, e.g. _@{} ena..._'.format(bot_username, bot_username),
            parse_mode=ParseMode.MARKDOWN
        )

    def inlinequery(self, bot, update):
        query = update.inline_query.query

        if len(query) >= settings.TELEGRAM_SEARCH_MIN_CHAR_COUNT:

            try:
                lookup = self.search_topics(query)

                if lookup:

                    results = list()

                    for record in lookup[:settings.TELEGRAM_SEARCH_RESULTS_LIMIT]:

                        results.append(
                            InlineQueryResultArticle(

                                id=uuid.uuid4(),
                                title=record['title'],
                                description=utils.collapse_newlines(record['body'])[:settings.SEARCH_PREVIEW_LENGTH],
                                url=record['url'],

                                input_message_content=InputTextMessageContent(

                                    message_text='*{}*\n\n{}\n\n*URL:* {}\n_Reply to this message to post a comment on Infinity._'.format(
                                        record['title'], record['body'], record['url']),
                                    parse_mode=ParseMode.MARKDOWN,
                                    disable_web_page_preview=True

                                ),
                            )
                        )

                    bot.answerInlineQuery(update.inline_query.id, results, cache_time=0)

                else:
                    update.inline_query.answer([])

            except Exception as e:
                logger.error(e)
                update.inline_query.answer([])


def main():

    agent = Agent(settings.TELEGRAM_BOT_TOKEN)

    agent.router.add_handler(CommandHandler('start', agent.start))
    agent.router.add_handler(InlineQueryHandler(agent.inlinequery))

    agent.run()

if __name__ == '__main__':
    main()
