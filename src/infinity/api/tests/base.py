# coding: utf-8
# flake8: noqa
import json
from unittest import TestCase

from mock import patch

from infinity.api.base import API


class APIMixin(TestCase):
    def create_api_client(self):
        """Returns dummy api client"""
        api = API(base_url='http://example.com/api/v1')
        return api


class AuthenticatedAPIMixin(APIMixin):
    def create_api_client(self):
        api = super(AuthenticatedAPIMixin, self).create_api_client()
        api.session.api_token = 'test_token'
        api.session.user = {}
        return api


def create_api_response(status_code, content=None, headers=None):
    """Returns MockResponse with parameters from arguments"""
    return MockResponse(status_code, content, headers)


def patch_api_request(status_code, json):
    """
    Decorator
    Patches requests.sessions.Session.send for mocking API requests
    """
    return patch(
        'requests.sessions.Session.send',
        return_value=create_api_response(status_code, json),
    )


class MockResponse(object):
    def __init__(self, status_code, content=None, headers=None):
        self.content = content
        self.status_code = status_code
        self.headers = headers or {}

    def json(self):
        if isinstance(self.content, dict):
            return self.content
        return json.loads(self.content)
