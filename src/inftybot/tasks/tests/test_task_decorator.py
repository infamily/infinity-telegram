# coding: utf-8
from unittest import TestCase

from inftybot.tasks.base import task


@task
def func(*args, **kwargs):
    return args, kwargs


class TaskDecoratorTestCase(TestCase):
    def test_bot_passed_in_kwargs(self):
        args, kwargs = func()
        self.assertIn('bot', kwargs)

    def test_chat_storage_passed_in_kwargs(self):
        args, kwargs = func()
        self.assertIn('chat_storage', kwargs)

    def test_user_storage_passed_in_kwargs(self):
        args, kwargs = func()
        self.assertIn('user_storage', kwargs)
