# coding: utf-8
from uuid import uuid4

import telegram

from inftybot.intents.base import BaseIntent
from inftybot.api.base import API


class SearchTopicsInlineQuery_(BaseIntent):
    def handle(self):
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

        return results


def parse_query(query):
    """
    Parse query for lang and query parts
    :return:
    """
    if query[2] == ':':
        lang, query = query.split(':', 1)
    else:
        lang = None

    return lang, query


class BaseInlineQuery(BaseIntent):
    def __init__(self, *args, **kwargs):
        super(BaseInlineQuery, self).__init__(*args, **kwargs)
        lang, query = self.parse_query()
        self.lang = lang
        self.query = query

    def parse_query(self):
        """
        Parse ```update.inline_query.query``` for lang and query parts
        :return:
        """
        return parse_query(self.update.inline_query.query)

    def handle(self):
        raise NotImplementedError


class SearchTopicsInlineQuery(BaseInlineQuery):
    def get_params(self):
        params = {'search': self.query}
        if self.lang:
            params.update({'lang': self.lang})
        return params

    def handle(self):
        results = []

        if not self.query:
            return results

        params = self.get_params()
        search_result = self.api.client.topics.get(**params)
        pass
