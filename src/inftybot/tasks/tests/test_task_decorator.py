# coding: utf-8
from django.test import TestCase
from telegram import Bot

from inftybot.tasks.base import task


@task
def func(bot, *args, **kwargs):
    return bot, args, kwargs


class TaskDecoratorTestCase(TestCase):
    def test_bot_passed_in_first_argument(self):
        bot, args, kwargs = func()
        self.assertIsInstance(bot, Bot)
