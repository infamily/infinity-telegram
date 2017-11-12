# coding: utf-8
from uuid import uuid4

import telegram
from telegram import InputTextMessageContent, ParseMode
from telegram.ext import InlineQueryHandler

from inftybot import config
from inftybot.intents import constants
from inftybot.intents.base import BaseIntent


def parse_query(query):
    """
    Parse query for lang and query parts
    :return:
    """
    try:
        lang, query = query.split(':', 1)
    except ValueError:
        lang = None

    return lang, query


def format_message_text(result):
    template = "`{type}:` *{title}*\n\n{body}\n\n*URL:* {url}\n" \
               "_Reply to this message to post a comment on Infinity._"

    return template.format(
        type=constants.TOPIC_TYPE_CHOICES.get(result.get('type')),
        title=result.get('title'),
        body=result.get('body'),
        url=result.get('url')
    )


def process_result(result):
    description = result.get('body', '')[:config.SEARCH_PREVIEW_LENGTH]
    message_text = format_message_text(result)

    return telegram.InlineQueryResultArticle(
        id=uuid4(),
        title=result.get('title'),
        description='{} ...'.format(description) if description else '',
        url=result.get('url'),
        input_message_content=InputTextMessageContent(
            message_text=message_text,
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
        )
    )


class BaseInlineQuery(BaseIntent):
    def __init__(self, **kwargs):
        super(BaseInlineQuery, self).__init__(**kwargs)
        lang, query = self.parse_query()
        self.lang = lang
        self.query = query

    def handle_error(self, error):
        raise NotImplementedError

    def parse_query(self):
        """
        Parse ```update.inline_query.query``` for lang and query parts
        :return:
        """
        return parse_query(self.update.inline_query.query)


class SearchTopicsInlineIntent(BaseInlineQuery):
    @classmethod
    def get_handler(cls):
        return InlineQueryHandler(cls.as_callback())

    def get_params(self):
        params = {'search': self.query}
        if self.lang:
            params.update({'lang': self.lang})
        return params

    def handle(self):
        results = []

        if not self.query:
            return results

        if not len(self.query) > config.SEARCH_MIN_CHAR_COUNT:
            return results

        params = self.get_params()
        response = self.api.client.topics.get(**params)

        # todo handle limit via query
        results = [process_result(r) for r in response['results'][0:config.SEARCH_RESULTS_LIMIT]]

        self.update.inline_query.answer(results, cache_time=config.INLINE_QUERY_CACHE_TIME)
