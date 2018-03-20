# coding: utf-8
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.utils.translation import gettext_lazy

_ = gettext_lazy


class ChatQuerySet(models.QuerySet):
    def create(self, **kwargs):
        instance = super(ChatQuerySet, self).create(**kwargs)
        instance.ensure_chat_data()
        return instance


class ChatManager(models.Manager):
    pass


class Chat(models.Model):
    """Chat model"""
    TYPE_PRIVATE = 'private'
    TYPE_GROUP = 'group'
    TYPE_CHANNEL = 'channel'

    TYPE_CHOICES = (
        (TYPE_CHANNEL, _('Channel')),
        (TYPE_GROUP, _('Group')),
        (TYPE_PRIVATE, _('Private')),
    )

    objects = ChatManager.from_queryset(ChatQuerySet)()
    id = models.BigAutoField(primary_key=True)
    type = models.CharField(max_length=24, choices=TYPE_CHOICES, verbose_name=_('Chat type'))

    def ensure_chat_data(self):
        try:
            return self.chatdata
        except ChatData.DoesNotExist:
            return ChatData.objects.create(chat=self)


class ChatData(models.Model):
    """Chat data model"""
    chat = models.OneToOneField('chats.Chat', on_delete=models.CASCADE, verbose_name=_('Chat reference'))
    data = JSONField(verbose_name=_('Session data'), blank=True, null=False, default={})
