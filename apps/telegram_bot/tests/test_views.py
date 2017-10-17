# coding: utf-8
import json

from flask import current_app, jsonify
from flask_testing import TestCase
from mock import patch, MagicMock

from app import create_app


class WebhookHandlerTestCase(TestCase):
    DIRECT_MESSAGE_PAYLOAD = {
        'update_id': 941115952,
        'message': {
            'message_id': 7,
            'from': {
                'id': 317865952, 'is_bot': False,
                'first_name': 'Kuznetsov',
                'last_name': 'Eugene',
                'username': 'e_kuznetsov',
                'language_code': 'en-US'
            },
            'chat': {
                'id': 317865952, 'first_name': 'Kuznetsov',
                'last_name': 'Eugene', 'username': 'e_kuznetsov',
                'type': 'private'
            },
            'date': 1508256396,
            'text': 'message'
        }
    }

    def create_app(self):
        app = create_app()
        app.extensions['telegram_bot'].bot.webhook_handler = MagicMock(return_value='{}')
        return app

    def test_telegram_direct_message_executes_webhook_handler(self):
        self.client.post(
            '/telegram/webhook', data=json.dumps(self.DIRECT_MESSAGE_PAYLOAD), content_type='application/json'
        )
        self.assertEquals(1, self.app.extensions['telegram_bot'].bot.webhook_handler.call_count)
