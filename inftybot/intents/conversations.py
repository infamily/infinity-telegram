# coding: utf-8
from telegram.ext import ConversationHandler

from inftybot.intents import base, commands, messages, states


class BaseConversationIntent(base.BaseIntent):
    def handle(self, *args, **kwargs):
        """No direct handling assumed"""
        pass


class LoginConversationIntent(BaseConversationIntent):
    @classmethod
    def get_handler(cls):
        return ConversationHandler(
            entry_points=[commands.LoginCommandIntent.get_handler()],
            states={
                states.AUTH_STATE_EMAIL: [messages.AuthEmailIntent.get_handler()],
                states.AUTH_STATE_CAPTCHA: [messages.AuthCaptchaIntent.get_handler()],
                states.AUTH_STATE_PASSWORD: [messages.AuthOTPIntent.get_handler()],
            },
            fallbacks=[commands.CancelCommandIntent.get_handler()],
        )


class TopicConversationIntent(BaseConversationIntent):
    @classmethod
    def get_handler(cls):
        return ConversationHandler(
            entry_points=[commands.TopicCreateCommandIntent.get_handler()],
            states={
                states.TOPIC_STATE_TITLE: [messages.TopicTitleIntent.get_handler()],
                states.TOPIC_STATE_BODY: [messages.TopicBodyIntent.get_handler()],
            },
            fallbacks=[
                commands.TopicDoneCommandIntent.get_handler(),
                commands.CancelCommandIntent.get_handler(),
            ],
        )
