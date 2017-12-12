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

    @captcha.setter
    def captcha(self, value):
        chat_data = getattr(self, 'chat_data', {})
        chat_data['captcha'] = value


class AuthEmailIntent(CaptchaMixin, BaseMessageIntent):
    def validate(self):
        parts = self.update.message.text.split('@')

        if len(parts) != 2:
            raise ValidationError("Please, enter valid email")

    def handle(self, *args, **kwargs):
        user = User()
        user.email = self.update.message.text

        captcha = self.api.client.otp.signup.get()

        self.user = user
        self.captcha = captcha

        self.update.message.reply_text(_('Please, solve the captcha:'))

        captcha_url = urllib.parse.urljoin(config.INFTY_SERVER_URL, captcha['image_url'])
        self.bot.sendPhoto(
            chat_id=self.update.message.chat_id,
            photo=captcha_url
        )

        return states.AUTH_STATE_CAPTCHA


class AuthCaptchaIntent(CaptchaMixin, AuthenticationMixin, BaseMessageIntent):
    def validate(self):
        payload = {
            'email': self.user.email,
            'captcha_0': self.captcha['key'],
            'captcha_1': self.update.message.text,
        }

        try:
            response = self.api.client.otp.signup.post(
                data=payload
            )
        except HttpClientError as e:
            response = getattr(e, 'response')
            response_data = response.json()
            errors = response_data.pop('errors', '')
            self.chat_data['captcha'] = response_data
            raise CaptchaValidationError(
                errors or _("Bad captcha. Please, solve again"),
                captcha=response_data
            )

        # it is not proper way
        # to assign the state on the validation stage
        # todo
        self.set_api_authentication(response['token'])

    def handle_error(self, error):
        self.update.message.reply_text(_(error.message))

        captcha_url = urllib.parse.urljoin(config.INFTY_SERVER_URL, error.captcha['image_url'])
        self.bot.sendPhoto(
            chat_id=self.update.message.chat_id,
            photo=captcha_url
        )

    def handle(self, *args, **kwargs):
        self.update.message.reply_text(_("Ok. Then, enter the OTP"))
        return states.AUTH_STATE_PASSWORD


class AuthOTPIntent(CaptchaMixin, AuthenticatedMixin, BaseMessageIntent):
    def validate(self):
        try:
            self.api.client.otp.login.post(data={
                'password': self.update.message.text,
            })
            assert True
        except HttpClientError:
            raise ValidationError(
                _("Wrong authentication credentials")
            )

    def handle_error(self, error):
        self.update.message.reply_text(_("Login failed"))

    def handle(self, *args, **kwargs):
        self.update.message.reply_text(_('Login success'))
        return states.STATE_END


class LoginCommandIntent(BaseCommandIntent):
    @classmethod
    def get_handler(cls):
        return CommandHandler("login", cls.as_callback(), pass_chat_data=True)

    def handle(self, *args, **kwargs):
        self.update.message.reply_text(_("What's your email?"))
        return states.AUTH_STATE_EMAIL


class LoginConversationIntent(BaseConversationIntent):
    @classmethod
    def get_handler(cls):
        return ConversationHandler(
            entry_points=[LoginCommandIntent.get_handler()],
            states={
                states.AUTH_STATE_EMAIL: [AuthEmailIntent.get_handler()],
                states.AUTH_STATE_CAPTCHA: [AuthCaptchaIntent.get_handler()],
                states.AUTH_STATE_PASSWORD: [AuthOTPIntent.get_handler()],
            },
            fallbacks=[CancelCommandIntent.get_handler()],
        )
