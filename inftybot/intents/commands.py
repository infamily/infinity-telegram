# coding: utf-8
from inftybot.intents.base import BaseIntent


class StartCommand(BaseIntent):
    """
    Handler for /start intent
    """
    def handle(self):
        return "Ok, let's start"


