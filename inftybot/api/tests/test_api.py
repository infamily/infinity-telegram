# coding: utf-8
from unittest import TestCase

from inftybot.api.tests.base import APIMixin
from inftybot.models import User


class APISetUserTestCase(APIMixin, TestCase):
    def setUp(self):
        self.api = self.create_api_client()

    def test_set_user_updates_session_headers(self):
        user = User()
        user.token = 'test_token'
        self.api.user = user
        self.assertEqual(
            self.api.session.headers['Authorization'],
            'Token test_token'
        )
