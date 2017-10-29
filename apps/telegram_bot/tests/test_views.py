# coding: utf-8
import json

from flask_testing import TestCase
from mock import MagicMock

from app import create_app
from apps.telegram_bot.base import EXTENSION_NAME


class WebhookHandlerTestCase(TestCase):
    def create_app(self):
        app = create_app()
        app.extensions[EXTENSION_NAME].dispatcher = MagicMock(return_value='{}')
        return app

    def test_telegram_direct_message_executes_webhook_handler(self):
        payload = {'test': 'complete'}
        self.client.post(
            '/telegram/webhook', data=json.dumps(payload), content_type='application/json'
        )
        name, args, kwargs = self.app.extensions[EXTENSION_NAME].dispatcher.method_calls[0]
        self.assertEquals('process_update', name)
        self.assertEquals(payload, args[0])
