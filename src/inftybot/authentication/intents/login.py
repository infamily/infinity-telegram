# coding: utf-8
import gettext
import urllib.parse

from slumber.exceptions import HttpClientError
from telegram.ext import CommandHandler

import inftybot.authentication.states
import inftybot.core.states
from contrib.telegram.ext import ConversationHandler
from inftybot import config
from inftybot.authentication.intents.base import AuthenticationMixin, logout, login
from inftybot.authentication.models import Session
from inftybot.core.exceptions import ValidationError, CaptchaValidationError
from inftybot.core.intents.base import (
    BaseCommandIntent, BaseConversationIntent, BaseMessageIntent,
    BaseIntent)
from inftybot.core.intents.cancel import CancelCommandIntent

_ = gettext.gettext


class LoginLogoutIntent(BaseCommandIntent):
    """Base class for login/logout intents"""
    def _check_session(self):
        try:
            return self.current_user.session and len(self.current_user.session.session_data['token'])
        except (Session.DoesNotExist, KeyError):
            return False


class CaptchaMixin(BaseIntent):
    """Adds captcha-specific methods"""
    def get_captcha(self):
        current_chat = self.get_current_chat()
        return current_chat.chatdata.data.get('captcha', {})

    def set_captcha(self, value):
        current_chat = self.get_current_chat()
        current_chat.chatdata.data['captcha'] = value
        current_chat.chatdata.save()

    def clear_captcha(self):
        current_chat = self.get_current_chat()
        try:
            del current_chat.chatdata.data['captcha']
        except KeyError:
            pass


class AuthEmailIntent(CaptchaMixin, BaseMessageIntent):
    def validate(self):
        parts = self.update.message.text.split('@')

        if len(parts) != 2:
            raise ValidationError("Please, enter valid email")

    def handle(self, *args, **kwargs):
        user = self.get_current_user()
        user.email = self.update.message.text
        user.save()

        captcha = self.api.client.captcha.get()
        self.set_captcha(captcha)

        self.update.message.reply_text(_('Please, solve the captcha:'))

        captcha_url = urllib.parse.urljoin(config.INFTY_SERVER_URL, captcha['image_url'])
        self.bot.sendPhoto(
            chat_id=self.update.message.chat_id,
            photo=captcha_url
        )

        return inftybot.authentication.states.AUTH_STATE_CAPTCHA


class AuthCaptchaIntent(CaptchaMixin, BaseMessageIntent):
    def before_validate(self, *args, **kwargs):
        self.current_user.ensure_session()

    def validate(self):
        captcha = self.get_captcha()

        payload = {
            'email': self.current_user.email,
            'captcha': {
                'hashkey': captcha['key'],
                'response': self.update.message.text,
            }
        }

        try:
            self.api.client.signup.post(
                data=payload
            )
        except HttpClientError as e:
            raise CaptchaValidationError(
                _("Bad captcha. Please, solve again"),
            )

    def handle_error(self, error):
        captcha = self.api.client.captcha.get()
        self.set_captcha(captcha)

        self.update.message.reply_text(_(error.message))
        captcha_url = urllib.parse.urljoin(config.INFTY_SERVER_URL, captcha['image_url'])
        self.bot.sendPhoto(
            chat_id=self.update.message.chat_id,
            photo=captcha_url
        )

    def handle(self, *args, **kwargs):
        self.clear_captcha()
        self.update.message.reply_text(_("Ok. Then, enter the OTP"))
        return inftybot.authentication.states.AUTH_STATE_PASSWORD


class AuthOTPIntent(AuthenticationMixin, BaseMessageIntent):
    def before_validate(self, *args, **kwargs):
        self.current_user.ensure_session()

    def validate(self):
        try:
            payload = {
                'email': self.current_user.email,
                'one_time_password': self.update.message.text,
            }
            response = self.api.client.signin.post(data=payload)
        except HttpClientError as e:
            raise ValidationError(
                _("Wrong authentication credentials")
            )
        else:
            self.chat_data['token'] = response['auth_token']

    def handle_error(self, error):
        self.update.message.reply_text(_("Login failed"))

    def handle(self, *args, **kwargs):
        login(self.current_user, self.chat_data['token'])
        self.update.message.reply_text(_('Login success'))
        return inftybot.core.states.STATE_END


class LoginCommandIntent(LoginLogoutIntent):
    @classmethod
    def get_handler(cls):
        return CommandHandler("login", cls.as_callback(), pass_chat_data=True, pass_user_data=True)

    def handle(self, *args, **kwargs):
        if self._check_session():
            self.update.message.reply_text(_("I know you!"))
            return inftybot.core.states.STATE_END
        else:
            self.update.message.reply_text(_("What's your email?"))
            return inftybot.authentication.states.AUTH_STATE_EMAIL


class LogoutCommandIntent(LoginLogoutIntent):
    @classmethod
    def get_handler(cls):
        return CommandHandler("logout", cls.as_callback(), pass_chat_data=True, pass_user_data=True)

    def handle(self, *args, **kwargs):
        if not self._check_session():
            self.update.message.reply_text(_("?"))
            return inftybot.core.states.STATE_END

        logout(self.current_user)
        self.update.message.reply_text(_("See you!"))
        return inftybot.core.states.STATE_END


class LoginConversationIntent(BaseConversationIntent):
    @classmethod
    def get_handler(cls):
        return ConversationHandler(
            entry_points=[LoginCommandIntent.get_handler()],
            states={
                inftybot.authentication.states.AUTH_STATE_EMAIL: [AuthEmailIntent.get_handler()],
                inftybot.authentication.states.AUTH_STATE_CAPTCHA: [AuthCaptchaIntent.get_handler()],
                inftybot.authentication.states.AUTH_STATE_PASSWORD: [AuthOTPIntent.get_handler()],
            },
            fallbacks=[CancelCommandIntent.get_handler()],
        )
