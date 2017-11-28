# coding: utf-8
from unittest import TestCase

from inftybot.api.tests.base import APIMixin
from inftybot.models import User
from inftybot.tests.base import BotMixin, mock_update
from inftybot.utils import update_from_dict


class UserMixin(TestCase):
    def setUp(self):
        super(UserMixin, self).setUp()
        self.user = User()
        self.user.email = 'email@example.com'
        self.user.token = 'test_token'


class BaseIntentTestCase(BotMixin, APIMixin, TestCase):
    intent_cls = None

    def setUp(self):
        super(BaseIntentTestCase, self).setUp()
        self.bot = self.create_bot()
        self.api = self.create_api_client()

    def create_intent(self, update, **kwargs):
        update = update_from_dict(self.bot, update)
        mock_update(update)
        intent = self.intent_cls(
            bot=self.bot, update=update,
            api=self.api, **kwargs
        )
        return intent
