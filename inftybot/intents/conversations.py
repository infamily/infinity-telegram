# coding: utf-8
from telegram.ext import ConversationHandler

from inftybot.intents.base import BaseIntent
from inftybot.intents.commands import LoginCommandIntent, CancelCommandIntent
from inftybot.intents.messages import AuthEmailIntent, AuthCaptchaIntent, AuthOTPIntent
from inftybot.intents.states import AUTH_STATE_EMAIL, AUTH_STATE_CAPTCHA, AUTH_STATE_PASSWORD


class BaseConversationIntent(BaseIntent):
    def handle(self, *args, **kwargs):
        """No direct handling assumed"""
        pass


class LoginConversationIntent(BaseConversationIntent):
    @classmethod
    def get_handler(cls):
        return ConversationHandler(
            entry_points=[LoginCommandIntent.get_handler()],
            states={
                AUTH_STATE_EMAIL: [AuthEmailIntent.get_handler()],
                AUTH_STATE_CAPTCHA: [AuthCaptchaIntent.get_handler()],
                AUTH_STATE_PASSWORD: [AuthOTPIntent.get_handler()],
            },
            fallbacks=[CancelCommandIntent.get_handler()]
        )
