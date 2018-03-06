# coding: utf-8
from django.core.cache import caches
from django.core.exceptions import ImproperlyConfigured
from telegram.ext import ConversationHandler as BaseConversationHandler


def get_conversation_storage():
    try:
        return caches['conversations']
    except KeyError:
        raise ImproperlyConfigured("You should specify 'conversation' cache backed")


class ConversationStorage(object):
    def __init__(self):
        self._storage = get_conversation_storage()

    def get(self, key, default=None):
        return self._storage.get(key, default)

    def set(self, key, value):
        return self._storage.set(key, value)

    def __getitem__(self, key):
        return self.get(key)

    def __setitem__(self, key, value):
        return self.set(key, value)

    def __delitem__(self, key):
        return self._storage.delete(key)


class ConversationHandler(BaseConversationHandler):
    def __init__(self, *args, **kwargs):
        super(ConversationHandler, self).__init__(*args, **kwargs)
        self.conversations = ConversationStorage()
