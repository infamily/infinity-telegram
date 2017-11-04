# coding: utf-8
from telegram.ext import MessageHandler, Filters

from inftybot.intents.base import BaseIntent
from inftybot.intents.exceptions import ValidationError
from inftybot.intents.states import AUTH_STATE_CAPTCHA, AUTH_STATE_PASSWORD, STATE_END
from inftybot.models import User


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
        if '@' not in self.update.message.text:
            raise ValidationError("Please, enter valid email")

    def handle(self, *args, **kwargs):
        user = User()
        user.email = self.update.message.text
        captcha = None

        self.data.user = user
        self.data.captcha = captcha

        self.update.message.reply_text('Please, solve the captcha:')
        # self.bot.sendPhoto(
        #     chat_id=self.update.message.chat_id,
        #     photo=None
        # )
        return AUTH_STATE_CAPTCHA


class AuthCaptchaIntent(BaseMessageIntent):
    def validate(self):
        # validate captcha
        pass

    def handle(self, *args, **kwargs):
        user = self.data.user
        self.update.message.reply_text("Ok. Then, enter the OTP".format(user.email))
        return AUTH_STATE_PASSWORD


class AuthOTPIntent(BaseMessageIntent):
    def validate(self):
        # validate otp
        pass

    def handle(self, *args, **kwargs):
        try:
            assert True
            self.update.message.reply_text('Login success')
            return STATE_END
        except AssertionError:
            self.update.message.reply_text("Login failed")

        self.update.message.reply_text("OTP?")
