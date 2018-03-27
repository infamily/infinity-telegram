# coding: utf-8
import json

from django.test import TestCase
from django.urls import reverse

from inftybot.core.tests.base import load_tg_updates, BotMixin

tg_updates = load_tg_updates()


class WebhookTestCase(BotMixin, TestCase):
    def setUp(self):
        super(WebhookTestCase, self).setUp()

    def test_start_command_webhook_return_202_with_no_content(self):
        payload = tg_updates['START_COMMAND']
        url = reverse('inftybot:webhook')
        response = self.client.post(url, data=json.dumps(payload), content_type='text/json')
        self.assertEqual(response.status_code, 202)
        self.assertEqual(len(response.content), 0)
