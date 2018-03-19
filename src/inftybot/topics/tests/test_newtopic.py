# coding: utf-8
# flake8: noqa
from inftybot.core.states import STATE_END
from inftybot.core.tests.base import load_tg_updates, load_api_responses
from inftybot.topics import states
from inftybot.topics.intents import newtopic
from inftybot.topics.tests.test_basetopic import TopicIntentTestCase

updates = load_tg_updates()
api_responses = load_api_responses()


class NewTopicIntentTestCase(TopicIntentTestCase):
    intent_cls = newtopic.TopicCreateCommandIntent
    update = updates['NEW_TOPIC']

    def test_intent_return_proper_new_state(self):
        new_state = self.intent()
        self.assertEqual(new_state, states.TOPIC_STATE_TYPE)

    def test_intent_handler_set_new_topic(self):
        self.intent()
        topic = self.intent.get_topic()
        self.assertGreater(len(topic), 0)


class InputTypeIntentTestCase(TopicIntentTestCase):
    intent_cls = newtopic.InputTypeIntent
    update = updates['TOPIC_TYPE_NEED']

    def test_intent_return_proper_new_state(self):
        new_state = self.intent()
        self.assertEqual(new_state, states.TOPIC_STATE_CATEGORY)

    def test_intent_handler_update_topic_title(self):
        self.intent()
        topic = self.intent.get_topic()
        self.assertEqual(topic['type'], 0)


class InputCategoryIntentCase(TopicIntentTestCase):
    intent_cls = newtopic.InputCategoryIntent
    update = updates['TOPIC_CATEGORIES']

    def test_intent_return_proper_new_state(self):
        intent = self.create_intent(self.update)
        new_state = intent()
        self.assertEqual(new_state, states.TOPIC_STATE_TITLE)

    def test_intent_handler_update_topic_category(self):
        self.intent()
        topic = self.intent.get_topic()
        self.assertEqual(topic['categories_names'], ['general', 'medicine'])


class InputTitleIntentTestCase(TopicIntentTestCase):
    intent_cls = newtopic.InputTitleIntent
    update = updates['TOPIC_TITLE']

    def test_intent_return_proper_new_state(self):
        intent = self.create_intent(self.update)
        new_state = intent()
        self.assertEqual(new_state, states.TOPIC_STATE_BODY)

    def test_intent_handler_update_topic_title(self):
        self.intent()
        topic = self.intent.get_topic()
        self.assertEqual(topic['title'], 'Topic title')


class InputBodyIntentTestCase(TopicIntentTestCase):
    intent_cls = newtopic.InputBodyIntent
    update = updates['TOPIC_BODY']

    def test_intent_return_proper_new_state(self):
        intent = self.create_intent(self.update)
        new_state = intent()
        self.assertEqual(new_state, STATE_END)

    def test_intent_handler_update_topic_title(self):
        self.intent()
        topic = self.intent.get_topic()
        self.assertEqual(topic['body'], 'Topic body')
