# coding: utf-8
import unittest.mock as mock

from autofixture import AutoFixture
from django.test import TestCase
from telegram import Bot

from infinity.api.tests.base import patch_api_request
from inftybot.chats.models import Chat
from inftybot.core.tests.base import load_api_responses
from inftybot.notifications.tasks import notify_subscribers_about_new_topic

api_responses = load_api_responses()


class NotifySubscribersTaskTestCase(TestCase):
    def setUp(self):
        super(NotifySubscribersTaskTestCase, self).setUp()
        self.subscribed_chats = AutoFixture(Chat).create(2)
        self.unsubscribed_chats = AutoFixture(Chat).create(2)

        for chat in self.subscribed_chats[0:1]:
            chat.categories_set.create(categories=['test1', 'test2'])

        for chat in self.subscribed_chats[1:]:
            chat.categories_set.create(categories=['тест1', 'тест2'])

    def build_test_event(self, **kwargs):
        event = {
            'topic_id': 1,
        }
        event.update(kwargs)
        return event

    @patch_api_request(200, api_responses['TOPIC_DETAIL'])
    @mock.patch.object(Bot, 'send_message')
    def test_attempt_to_notify_every_subscribed_chat(self, mock, *args):
        event = self.build_test_event()
        notify_subscribers_about_new_topic(**{'event': event})
        notified_chats_ids = [c[0][0] for c in mock.call_args_list]
        subscribed_chats_ids = [c.id for c in self.subscribed_chats]
        self.assertTrue(all(cid in subscribed_chats_ids for cid in notified_chats_ids))

    @patch_api_request(200, api_responses['TOPIC_DETAIL'])
    @mock.patch.object(Bot, 'send_message')
    def test_unsubscribed_chats_was_not_notified(self, mock, *args):
        event = self.build_test_event()
        notify_subscribers_about_new_topic(**{'event': event})
        notified_chats_ids = [c[0][0] for c in mock.call_args_list]
        unsubscribed_chats_ids = [c.id for c in self.unsubscribed_chats]
        self.assertFalse(all(cid in unsubscribed_chats_ids for cid in notified_chats_ids))
