# coding: utf-8
# flake8: noqa
import json

from django.forms import model_to_dict

from infinity.api.tests.base import patch_api_request
from inftybot.core.exceptions import ValidationError
from inftybot.core.tests.base import BaseIntentTestCase, UserMixin, create_user_from_update, create_chat_from_update, \
    load_tg_updates, load_api_responses
from inftybot.topics.constants import TOPIC_TYPE_NEED
from inftybot.topics.intents.base import TopicDoneCommandIntent
from inftybot.topics.models import Topic

updates = load_tg_updates()
api_responses = load_api_responses()


class TopicDoneTestCase(UserMixin, BaseIntentTestCase):
    intent_cls = TopicDoneCommandIntent
    INJECT_USER = True

    def test_model_invalid_topic_raises(self):
        update = updates['TOPIC_DONE']
        intent = self.create_intent(update)

        data = {'title': None, 'body': ''}
        intent.chat_data['topic'] = data

        with self.assertRaises(ValidationError):
            intent.validate()

    @patch_api_request(200, {})
    def test_valid_topic_calls_api_post(self, api_mock):
        update = updates['TOPIC_DONE']
        intent = self.create_intent(update)

        create_user_from_update(self.bot, update)

        topic = Topic()
        topic.title = 'Test title'
        topic.body = 'Test body'
        topic.type = TOPIC_TYPE_NEED

        intent(chat_data={'topic': topic})
        self.assertGreater(api_mock.call_count, 0)

    @patch_api_request(200, {})
    def test_valid_topic_api_request_params_ok(self, api_mock):
        update = updates['TOPIC_DONE']
        intent = self.create_intent(update)

        create_user_from_update(self.bot, update)
        chat = create_chat_from_update(self.bot, update)
        chat_data = chat.ensure_chat_data()

        topic = Topic()
        topic.title = 'Test title'
        topic.body = 'Test body'
        topic.type = TOPIC_TYPE_NEED

        chat_data.data['topic'] = model_to_dict(topic)
        chat_data.save()

        intent()
        request = api_mock.call_args[0][0]
        request_data = json.loads(request.body)

        self.assertIn('title', request_data.keys())
        self.assertIn('body', request_data.keys())
        self.assertIn('type', request_data.keys())

    def test_api_400_raises(self):
        pass
