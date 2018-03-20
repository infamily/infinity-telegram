# coding: utf-8
# flake8: noqa
from infinity.api.tests.base import patch_api_request
from inftybot.core.tests.base import load_tg_updates, load_api_responses
from inftybot.topics import states
from inftybot.topics.intents import edittopic
from inftybot.topics.tests.test_basetopic import TopicIntentTestCase

updates = load_tg_updates()
api_responses = load_api_responses()


class EditTopicIntentTestCase(TopicIntentTestCase):
    intent_cls = edittopic.TopicEditCommandIntent
    update = updates['EDIT_TOPIC']

    @patch_api_request(200, [])
    def test_intent_return_proper_new_state(self, api_response):
        new_state = self.intent()
        self.assertEqual(new_state, states.TOPIC_STATE_EDIT_CHOOSE_TOPIC)


class TopicChooseCallbackIntentTestCase(TopicIntentTestCase):
    intent_cls = edittopic.TopicChooseCallback
    update = updates['CHOOSE_TOPIC_CALLBACK']

    @patch_api_request(200, api_responses['TOPIC_DETAIL'])
    def test_intent_valid_data_fetch_and_set_topic_from_api(self, api_response):
        self.intent()
        fetched_topic = self.intent.get_topic_data()
        self.chat.chatdata.refresh_from_db()
        stored_topic = self.chat.chatdata.data['topic']
        self.assertEqual(fetched_topic['id'], stored_topic['id'])


class TopicPartChooseIntentTestCase(TopicIntentTestCase):
    intent_cls = edittopic.TopicPartChooseCallback
    update = updates['CHOOSE_TOPICPART_CALLBACK']

    @patch_api_request(200, api_responses['TOPIC_DETAIL'])
    def test_intent_valid_data_return_proper_state(self, api_response):
        new_state = self.intent()
        self.assertEqual(new_state, states.TOPIC_STATE_EDIT_INPUT)


class EditTitleChoosenTestCase(TopicIntentTestCase):
    intent_cls = edittopic.TopicEditIntent
    update = updates['TOPICPART_TITLE_CHOOSEN_CALLBACK']

    @patch_api_request(200, api_responses['TOPIC_DETAIL'])
    def test_intent_valid_data_return_proper_state(self, api_response):
        new_state = self.intent()
        self.assertEqual(new_state, states.TOPIC_STATE_TITLE)


class EditTypeChoosenTestCase(TopicIntentTestCase):
    intent_cls = edittopic.TopicEditIntent
    update = updates['TOPICPART_TYPE_CHOOSEN_CALLBACK']

    @patch_api_request(200, api_responses['TOPIC_DETAIL'])
    def test_intent_valid_data_return_proper_state(self, api_response):
        new_state = self.intent()
        self.assertEqual(new_state, states.TOPIC_STATE_TYPE)


class EditBodyChoosenTestCase(TopicIntentTestCase):
    intent_cls = edittopic.TopicEditIntent
    update = updates['TOPICPART_BODY_CHOOSEN_CALLBACK']

    @patch_api_request(200, api_responses['TOPIC_DETAIL'])
    def test_intent_valid_data_return_proper_state(self, api_response):
        new_state = self.intent()
        self.assertEqual(new_state, states.TOPIC_STATE_BODY)


class EditCategoryChoosenTestCase(TopicIntentTestCase):
    intent_cls = edittopic.TopicEditIntent
    update = updates['TOPICPART_CATEGORY_CHOOSEN_CALLBACK']

    @patch_api_request(200, api_responses['TOPIC_DETAIL'])
    def test_intent_valid_data_return_proper_state(self, api_response):
        new_state = self.intent()
        self.assertEqual(new_state, states.TOPIC_STATE_CATEGORY)


class EditTitleIntentTestCase(TopicIntentTestCase):
    intent_cls = edittopic.InputTitleIntent
    update = updates['TOPIC_TITLE']

    def test_intent_valid_data_return_proper_state(self):
        new_state = self.intent()
        self.assertEqual(new_state, states.TOPIC_STATE_EDIT)

    def test_intent_valid_data_field_changed(self):
        field_name = 'title'
        value_before = self.intent.get_topic_data()[field_name]
        self.intent()
        self.assertNotEqual(self.intent.get_topic_data()[field_name], value_before)


class EditTypeIntentTestCase(TopicIntentTestCase):
    intent_cls = edittopic.InputTypeIntent
    update = updates['TOPIC_TYPE_NEED']

    def test_intent_valid_data_return_proper_state(self):
        new_state = self.intent()
        self.assertEqual(new_state, states.TOPIC_STATE_EDIT)

    def test_intent_valid_data_field_changed(self):
        field_name = 'type'
        value_before = self.intent.get_topic_data()[field_name]
        self.intent()
        self.assertNotEqual(self.intent.get_topic_data()[field_name], value_before)


class EditBodyIntentTestCase(TopicIntentTestCase):
    intent_cls = edittopic.InputBodyIntent
    update = updates['TOPIC_BODY']

    def test_intent_valid_data_return_proper_state(self):
        new_state = self.intent()
        self.assertEqual(new_state, states.TOPIC_STATE_EDIT)

    def test_intent_valid_data_field_changed(self):
        field_name = 'body'
        value_before = self.intent.get_topic_data()[field_name]
        self.intent()
        self.assertNotEqual(self.intent.get_topic_data()[field_name], value_before)


class EditCategoryIntentTestCase(TopicIntentTestCase):
    intent_cls = edittopic.InputCategoryIntent
    update = updates['TOPIC_CATEGORIES']

    def test_intent_valid_data_return_proper_state(self):
        new_state = self.intent()
        self.assertEqual(new_state, states.TOPIC_STATE_EDIT)

    def test_intent_valid_data_field_changed(self):
        field_name = 'categories_names'
        value_before = self.intent.get_topic_data()[field_name]
        self.intent()
        self.assertNotEqual(self.intent.get_topic_data()[field_name], value_before)
