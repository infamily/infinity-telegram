# coding: utf-8
from inftybot.core.exceptions import AuthenticationError
from inftybot.core.intents.base import BaseIntent


class AuthenticationMixin(BaseIntent):
    """Adds authentiation-process specific methods"""

    def update_user_data(self, user):
        """
        Update current user_data from ```self.chat_data['user']``` and + authenticated_at
        """
        user_data = user.to_native()
        self.user_data.update(user_data)

    def set_api_authentication(self, user):
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
        self.set_api_authentication(self.user)

        if not self.is_authenticated:
            raise AuthenticationError("Please, /login first")

    def unauthenticate(self):
        self.user_data.clear()
        self.chat_data.clear()
