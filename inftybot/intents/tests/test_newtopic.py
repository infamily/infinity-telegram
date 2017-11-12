# coding: utf-8
import json
from unittest import TestCase, skip

from mock import patch

from inftybot.api import API
from inftybot.api.tests.base import patch_api_request
from inftybot.intents.constants import TOPIC_TYPE_NEED
from inftybot.intents.exceptions import ValidationError
from inftybot.intents.newtopic import TopicDoneCommandIntent
from inftybot.intents.tests.base import BaseIntentTestCase
from inftybot.models import Topic, User
from inftybot.tests.base import load_tg_updates, load_api_responses, BotMixin

updates = load_tg_updates()
api_responses = load_api_responses()


class NewTopicCommandIntentTestCase(BaseIntentTestCase):
    pass


class ChooseTopicTypeCallbackTestCase(BaseIntentTestCase):
    pass


class TopicDoneTestCase(BaseIntentTestCase):
    intent_cls = TopicDoneCommandIntent

    def test_model_invalid_topic_raises(self):
        intent = TopicDoneCommandIntent()
        topic = Topic()
        topic.title = None
        topic.body = ''

        intent.chat_data['topic'] = topic

        with self.assertRaises(ValidationError):
            intent.validate()

    @patch_api_request(200, {})
    def test_valid_topic_api_post_call(self, api_mock):
        update = updates['TOPIC_DONE']
        intent = self.create_intent(update)

        topic = Topic()
        topic.title = 'Test title'
        topic.body = 'Test body'
        topic.type = TOPIC_TYPE_NEED

        intent(chat_data={'topic': topic})
        request = api_mock.call_args[0][0]
        request_data = json.loads(request.body)

        self.assertIn('title', request_data.keys())
        self.assertIn('body', request_data.keys())
        self.assertIn('type', request_data.keys())

    def test_api_400_raises(self):
        pass


@skip
class UnmockedTopicDoneTestCase(BaseIntentTestCase):
    intent_cls = TopicDoneCommandIntent

    def create_api_client(self):
        return API()

    def test_valid_topic_api_post(self):
        update = updates['TOPIC_DONE']
        intent = self.create_intent(update)

        user = User()
        user.token = 'b7a515f02b0cda276d9c7925025d775daa5f5e45'

        topic = Topic()
        topic.title = 'Test title'
        topic.body = 'Test body'
        topic.type = TOPIC_TYPE_NEED

        intent(chat_data={'topic': topic, 'user': user})
        assert True
