# coding: utf-8
"""Infty2.0 REST API client"""
import logging

import slumber
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


def set_api_authorization_token(api_client, authorization_token):
    store = getattr(api_client, '_store')
    session = store['session']
    session.headers.update({
        'Authorization': 'Token {}'.format(authorization_token)
    })


def create_api_client(base_url=None, session=None, authorization_token=None, **kwargs):
    base_url = base_url or config.INFTY_API_URL
    api_client = APIClient(base_url, session=session, **kwargs)
    if authorization_token:
        set_api_authorization_token(api_client, authorization_token)
    return api_client


class API(object):
    """
    Class for acessing Infty REST API
    """

    def __init__(self, base_url=None, **kwargs):
        self.client = APIClient(base_url=base_url, **kwargs)
        self._data = {}

    def _update_session(self):
        # temporary solution because API returns token as HyperlinkedRelated field (as URL)
        session = self.user.ensure_session()
        token_url = session.session_data.get('token')

        try:
            token = list(filter(lambda v: v, token_url.split('/')))[-1]
        except (ValueError, AttributeError):
            token = None

        set_api_authorization_token(self.client, token)

    @property
    def user(self):
        return self._data.get('user', None)

    @user.setter
    def user(self, value):
        self._data['user'] = value
        self._update_session()

    @property
    def api_token(self):
        return self.user.session.session_data.get('token')

    @property
    def is_authenticated(self):
        return self.user and self.api_token is not None
