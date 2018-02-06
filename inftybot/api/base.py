# coding: utf-8
"""Infty2.0 REST API client"""
import logging

import slumber
from requests import Session
from slumber.exceptions import HttpClientError, HttpServerError

from inftybot import config

logger = logging.getLogger(__name__)


class APIResource(slumber.Resource):
    def _request(self, *args, **kwargs):
        try:
            return super(APIResource, self)._request(*args, **kwargs)
        except (HttpClientError, HttpServerError) as e:
            logger.error('API response error: {}, {}'.format(str(e), e.content))
            raise e


class APIClient(slumber.API):
    resource_class = APIResource


class API(object):
    """
    Class for acessing Infty REST API
    """
    def __init__(self, base_url=None, **kwargs):
        self.base_url = base_url or config.INFTY_API_URL
        self.session = Session()
        self.client = APIClient(self.base_url, session=self.session, **kwargs)
        self._data = {}

    def _update_session(self):
        # temporary solution because API returns token as HyperlinkedRelated field (as URL)
        token = list(filter(lambda v: v, self.user.token.split('/')))[-1]
        self.session.headers.update({
            'Authorization': 'Token {}'.format(token)
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
