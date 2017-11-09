# coding: utf-8
"""Infty2.0 REST API client"""
import slumber
from requests import Session

from inftybot import config


class API(object):
    """
    Class for acessing Infty REST API
    """
    def __init__(self, base_url=None, **kwargs):
        self.base_url = base_url or config.INFTY_API_URL
        self.session = Session()
        self.client = slumber.API(self.base_url, session=self.session, **kwargs)
        self._data = {}

    def _update_session(self):
        self.session.headers.update({
            'Authorization': 'Token {}'.format(self.user.token)
        })

    @property
    def user(self):
        return self._data.get('user', None)

    @user.setter
    def user(self, value):
        self._data['user'] = value
        self._update_session()

    @property
    def api_token(self):
        return self.user.token

    @property
    def is_authenticated(self):
        return self.user and self.api_token is not None
