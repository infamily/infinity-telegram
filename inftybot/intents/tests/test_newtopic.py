# coding: utf-8

from inftybot.intents.tests.base import BaseIntentTestCase
from inftybot.tests.base import load_tg_updates, load_api_responses

updates = load_tg_updates()
api_responses = load_api_responses()


class NewTopicCommandIntentTestCase(BaseIntentTestCase):
    pass


class ChooseTopicTypeCallbackTestCase(BaseIntentTestCase):
    pass
