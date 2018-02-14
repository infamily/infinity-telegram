# coding: utf-8
import gettext
import urllib.parse

from slumber.exceptions import HttpClientError
from telegram.ext import CommandHandler, ConversationHandler

from inftybot import config
from inftybot.intents import states
from inftybot.intents.base import AuthenticatedMixin, BaseCommandIntent, BaseConversationIntent, CancelCommandIntent, \
    BaseMessageIntent, AuthenticationMixin
from inftybot.intents.exceptions import ValidationError, CaptchaValidationError
from inftybot.models import User

_ = gettext.gettext


class CaptchaMixin(object):
    @property
    def captcha(self):
        chat_data = getattr(self, 'chat_data', {})
        return chat_data.get('captcha', {})

    def set_captcha(self, value, force_store=False):
        chat_data = getattr(self, 'chat_data', {})
        chat_data['captcha'] = value
        if force_store:
            chat_data.store(True)

    def clear_captcha(self):
        chat_data = getattr(self, 'chat_data', {})
        del chat_data['captcha']


class AuthEmailIntent(CaptchaMixin, BaseMessageIntent):
    def validate(self):
        parts = self.update.message.text.split('@')

        if len(parts) != 2:
            raise ValidationError("Please, enter valid email")

    def handle(self, *args, **kwargs):
        user = User()
        user.email = self.update.message.text

        captcha = self.api.client.captcha.get()

        self.set_user(user)
        self.set_captcha(captcha)

        self.update.message.reply_text(_('Please, solve the captcha:'))

        captcha_url = urllib.parse.urljoin(config.INFTY_SERVER_URL, captcha['image_url'])
        self.bot.sendPhoto(
            chat_id=self.update.message.chat_id,
            photo=captcha_url
        )

        return states.AUTH_STATE_CAPTCHA


class AuthCaptchaIntent(CaptchaMixin, BaseMessageIntent):
    def validate(self):
        payload = {
            'email': self.user.email,
            'captcha': {
                'hashkey': self.captcha['key'],
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

        # we need to force store data because it stored on handle_success
        # but this case is not success (see `inftybot.storage.store_data`)
        self.set_captcha(captcha, True)

        self.update.message.reply_text(_(error.message))
        captcha_url = urllib.parse.urljoin(config.INFTY_SERVER_URL, captcha['image_url'])
        self.bot.sendPhoto(
            chat_id=self.update.message.chat_id,
            photo=captcha_url
        )

    def handle(self, *args, **kwargs):
        self.clear_captcha()
        self.update.message.reply_text(_("Ok. Then, enter the OTP"))
        return states.AUTH_STATE_PASSWORD


class AuthOTPIntent(AuthenticationMixin, BaseMessageIntent):
    def validate(self):
        try:
            payload = {
                'email': self.user.email,
                'one_time_password': self.update.message.text,
            }
            response = self.api.client.signin.post(data=payload)
        except HttpClientError as e:
            raise ValidationError(
                _("Wrong authentication credentials")
            )
        else:
            user = self.user
            user.token = response['auth_token']
            self.set_user(user)

    def handle_error(self, error):
        self.update.message.reply_text(_("Login failed"))

    def handle(self, *args, **kwargs):
        self.update_user_data(self.user)
        self.update.message.reply_text(_('Login success'))
        return states.STATE_END


class LoginCommandIntent(BaseCommandIntent):
    @classmethod
    def get_handler(cls):
        return CommandHandler("login", cls.as_callback(), pass_chat_data=True, pass_user_data=True)

    def handle(self, *args, **kwargs):
        if self.user and self.user.token:
            self.update.message.reply_text(_("I know you!"))
            return states.STATE_END

        self.update.message.reply_text(_("What's your email?"))
        return states.AUTH_STATE_EMAIL


class LogoutCommandIntent(AuthenticatedMixin, BaseCommandIntent):
    @classmethod
    def get_handler(cls):
        return CommandHandler("logout", cls.as_callback(), pass_chat_data=True, pass_user_data=True)

    def handle(self, *args, **kwargs):
        self.unauthenticate()
        self.update.message.reply_text(_("See you!"))
        return states.STATE_END


class LoginConversationIntent(BaseConversationIntent):
    @classmethod
    def get_handler(cls):
        return ConversationHandler(
            entry_points=[LoginCommandIntent.get_handler(), LogoutCommandIntent.get_handler()],
            states={
                states.AUTH_STATE_EMAIL: [AuthEmailIntent.get_handler()],
                states.AUTH_STATE_CAPTCHA: [AuthCaptchaIntent.get_handler()],
                states.AUTH_STATE_PASSWORD: [AuthOTPIntent.get_handler()],
            },
            fallbacks=[CancelCommandIntent.get_handler()],
        )
