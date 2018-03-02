# coding: utf-8
import os

TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '')

INFTY_SERVER_URL = os.environ.get('INFTY_SERVER_URL', 'https://dev.wfx.io')
INFTY_API_URL = os.environ.get('INFTY_API_URL', 'https://dev.wfx.io')

# INFTY_SERVER_URL = os.environ.get('INFTY_SERVER_URL', 'http://localhost:8001')
# INFTY_API_URL = os.environ.get('INFTY_API_URL', 'http://localhost:8001/api/v1')

SEARCH_MIN_CHAR_COUNT = os.environ.get('SEARCH_MIN_CHAR_COUNT', 3)
SEARCH_RESULTS_LIMIT = os.environ.get('SEARCH_RESULTS_LIMIT', 50)
SEARCH_PREVIEW_LENGTH = os.environ.get('SEARCH_PREVIEW_LENGTH', 200)
INLINE_QUERY_CACHE_TIME = os.environ.get('INLINE_QUERY_CACHE_TIME', 0)

INTENTS = [
    'inftybot.core.intents.start.StartCommandIntent',
    'inftybot.core.intents.reset.ResetCommandIntent',
    'inftybot.core.intents.base.CancelCommandIntent',
    'inftybot.authentication.intents.login.LoginConversationIntent',

    # 'inftybot.intents.newtopic.TopicConversationIntent',
    # 'inftybot.intents.edittopic.TopicConversationIntent',
    # 'inftybot.intents.basetopic.TopicDoneCommandIntent',
    # 'inftybot.intents.search.SearchTopicsInlineIntent',
    # 'inftybot.intents.comment.ReplyIntent',
    # 'inftybot.intents.listcategories.ListCategoriesCommandIntent',
    # 'inftybot.intents.groupcategories.SetCategoriesCommandIntent',
    # 'inftybot.intents.groupcategories.GetCategoriesCommandIntent',
]

DISPATCHER_DEFAULT_CLASS = 'inftybot.dispatcher.Dispatcher'

TELEGRAM_ERROR_HANDLER = 'inftybot.error_callback'

JINJA_EXTENSIONS = [
    'inftybot.contrib.jinja2.ext.StringExtension',
]
