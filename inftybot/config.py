# coding: utf-8
import os


INFTY_API_URL = os.environ.get('INFTY_API_URL', 'https://test.wfx.io/api/v1/')
SEARCH_MIN_CHAR_COUNT = os.environ.get('SEARCH_MIN_CHAR_COUNT', 3)
SEARCH_RESULTS_LIMIT = os.environ.get('SEARCH_RESULTS_LIMIT', 50)
SEARCH_PREVIEW_LENGTH = os.environ.get('SEARCH_PREVIEW_LENGTH', 200)
INLINE_QUERY_CACHE_TIME = os.environ.get('INLINE_QUERY_CACHE_TIME', 0)
