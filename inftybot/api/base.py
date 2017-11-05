# coding: utf-8
"""Infty2.0 REST API client"""
import slumber

from inftybot import config


class API(object):
    """
    Class for acessing Infty REST API
    """
    def __init__(self, base_url=None, **kwargs):
        session = kwargs.pop('session', None)

        self.base_url = base_url or config.INFTY_API_URL
        self.client = slumber.API(self.base_url, **kwargs)
        self.session = Session(data=session)


class Session(object):
    """
    Represents current API session
    """
    def __init__(self, data=None):
        self._data = data or {}

    @property
    def user(self):
        return self._data.get('user', None)

    @user.setter
    def user(self, value):
        self._data['user'] = value

    @property
    def api_token(self):
        return self.user.token

    @property
    def is_authenticated(self):
        return self.user and self.api_token is not None
