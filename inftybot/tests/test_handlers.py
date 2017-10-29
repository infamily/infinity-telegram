# coding: utf-8
from unittest import TestCase

COMMAND_MESSAGE_PAYLOAD = {
    "message": {
        "chat": {
            "first_name": "Kuznetsov",
            "id": 317865952,
            "last_name": "Eugene",
            "type": "private",
            "username": "e_kuznetsov"
        },
        "date": 1509305066,
        "entities": [
            {
                "length": 4,
                "offset": 0,
                "type": "bot_command"
            }
        ],
        "from": {
            "first_name": "Kuznetsov",
            "id": 317865952,
            "is_bot": False,
            "language_code": "en-US",
            "last_name": "Eugene",
            "username": "e_kuznetsov"
        },
        "message_id": 19,
        "text": "/cmd"
    },
    "update_id": 739983003
}

DIRECT_MESSAGE_PAYLOAD = {
    "message": {
        "chat": {
            "first_name": "Kuznetsov",
            "id": 317865952,
            "last_name": "Eugene",
            "type": "private",
            "username": "e_kuznetsov"
        },
        "date": 1509305316,
        "from": {
            "first_name": "Kuznetsov",
            "id": 317865952,
            "is_bot": False,
            "language_code": "en-US",
            "last_name": "Eugene",
            "username": "e_kuznetsov"
        },
        "message_id": 20,
        "text": "test"
    },
    "update_id": 739983004
}


class WebhookHandlerTestCase(TestCase):
    pass


class DirectMessageWebhookTestCase(WebhookHandlerTestCase):
    pass
