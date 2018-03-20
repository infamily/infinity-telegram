# coding: utf-8
# flake8: noqa
from django.test import TestCase

from infinity.api.tests.base import APIMixin
from inftybot.authentication.models import ChatUser


class APISetUserTestCase(TestCase, APIMixin):
    def setUp(self):
        self.api = self.create_api_client()

    def test_set_user_updates_session_headers(self):
        user = ChatUser()
        user.save()
        user.ensure_session()
        user.session.session_data['token'] = 'test_token'
        self.api.user = user
        self.assertEqual(
            self.api.client._store['session'].headers['Authorization'],
            'Token test_token'
        )
