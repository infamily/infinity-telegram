# coding: utf-8
import gettext
import urllib.parse

from slumber.exceptions import HttpClientError
from telegram.ext import MessageHandler, Filters

from inftybot import config
from inftybot.intents import states
from inftybot.intents.base import BaseIntent
from inftybot.intents.exceptions import ValidationError, CaptchaValidationError
from inftybot.models import User

_ = gettext.gettext


class BaseMessageIntent(BaseIntent):
    @classmethod
    def get_handler(cls):
        return MessageHandler(
            Filters.text, cls.as_callback(), pass_chat_data=True
        )

    def handle_error(self, error):
        self.update.message.reply_text(error.message)


class AuthEmailIntent(BaseMessageIntent):
    def validate(self):
        parts = self.update.message.text.split('@')

        if len(parts) != 2:
            raise ValidationError("Please, enter valid email")

    def handle(self, *args, **kwargs):
        user = User()
        user.email = self.update.message.text

        captcha = self.api.client.otp.signup.get()

        self.chat_data['user'] = user
        self.chat_data['captcha'] = captcha

        self.update.message.reply_text(_('Please, solve the captcha:'))

        captha_url = urllib.parse.urljoin(config.INFTY_SERVER_URL, captcha['image_url'])

        self.bot.sendPhoto(
            chat_id=self.update.message.chat_id,
            photo=captha_url
        )

        return states.AUTH_STATE_CAPTCHA


class AuthCaptchaIntent(BaseMessageIntent):
    @property
    def user(self):
        return self.chat_data.get('user', None)

    @property
    def captcha(self):
        return self.chat_data.get('captcha', {})

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
            new_captcha = response.json()
            self.chat_data['captcha'] = new_captcha
            raise CaptchaValidationError(
                _("Bad captcha. Please, solve again"), captcha=new_captcha
            )

        # it is not proper way
        # to assign the state on the validation stage
        # todo
        self.user.token = response['token']

    def handle_error(self, error):
        self.update.message.reply_text(_(error.message))
        captha_url = urllib.parse.urljoin(config.INFTY_SERVER_URL, error.captcha['image_url'])
        self.bot.sendPhoto(
            chat_id=self.update.message.chat_id,
            photo=captha_url
        )

    def handle(self, *args, **kwargs):
        self.update.message.reply_text(_("Ok. Then, enter the OTP"))
        return states.AUTH_STATE_PASSWORD


class AuthOTPIntent(BaseMessageIntent):
    def validate(self):
        # validate otp
        pass

    def handle(self, *args, **kwargs):
        try:
            assert True
            self.update.message.reply_text(_('Login success'))
            return states.STATE_END
        except AssertionError:
            self.update.message.reply_text(_("Login failed"))

        self.update.message.reply_text(_("OTP?"))
