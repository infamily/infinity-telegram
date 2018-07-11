# coding: utf-8
from django.db.transaction import atomic

from inftybot.authentication.models import Session
from inftybot.core.exceptions import AuthenticationError
from inftybot.core.intents.base import BaseIntent


@atomic
def logout(user):
    """Logout chat user: clean its session object"""
    session = user.ensure_session()

    try:
        session.session_data = {}
        session.save()
    except Session.DoesNotExist:
        return


@atomic
def login(user, token, **params):
    """Login chat user: update session with API token, etc."""
    session = user.ensure_session()
    session_data = {'token': token}
    session_data.update(params)
    session.session_data = session_data
    session.save()


class AuthenticationMixin(BaseIntent):
    """Adds authentiation-process specific methods"""

    def set_api_authentication(self, user):
        """Set current user to the API wrapper"""
        self.api.user = user


class AuthenticatedMixin(AuthenticationMixin):
    """
    Intent with Infty API authentication
    Checks current user and its token
    """

    @property
    def is_authenticated(self):
        return self.api.is_authenticated

    def before_validate(self):
        super(AuthenticatedMixin, self).before_validate()
        self.set_api_authentication(self.current_user)

        if not self.is_authenticated:
            message = "Please, talk to @{} to login".format(self.bot.username)
            raise AuthenticationError(message)
