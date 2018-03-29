# coding: utf-8
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy

from inftybot.chats import constants

_ = gettext_lazy


class ChatQuerySet(models.QuerySet):
    def create(self, **kwargs):
        instance = super(ChatQuerySet, self).create(**kwargs)
        instance.ensure_chat_data()
        return instance

    def ensure_chat(self, **kwargs):
        pk = kwargs.get('id', kwargs.get('pk')) or None
        typ = kwargs.get('type', kwargs.get('typ')) or None
        instance, _ = self.get_or_create(pk=pk, type=typ)
        instance.ensure_chat_data()
        return instance

    def by_categories(self, categories):
        if not categories:
            return self.none()

        if not isinstance(categories, (list, tuple)):
            categories = [categories]

        categories = [c.lower() for c in categories]

        if all(isinstance(c, str) for c in categories):
            q = Q(categories__name__in=categories)
        else:
            q = Q(categories=categories)

        return self.filter(q)


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

    objects = models.Manager.from_queryset(ChatQuerySet)()
    id = models.BigAutoField(primary_key=True)
    type = models.CharField(max_length=24, choices=TYPE_CHOICES, verbose_name=_('Chat type'), db_index=True)
    categories = models.ManyToManyField('chats.ChatCategory')

    def ensure_chat_data(self):
        try:
            return self.chatdata
        except ChatData.DoesNotExist:
            return ChatData.objects.create(chat=self)


class ChatData(models.Model):
    """Chat data model"""
    chat = models.OneToOneField('chats.Chat', on_delete=models.CASCADE, verbose_name=_('Chat reference'))
    data = JSONField(verbose_name=_('Session data'), blank=True, null=False, default={})


class ChatCategory(models.Model):
    """Chat category model"""
    name = models.CharField(max_length=constants.MAX_CATEGORY_NAME_LENGTH, db_index=True)

    def save(self, *args, **kwargs):
        self.name = str(self.name).lower()
        return super(ChatCategory, self).save(*args, **kwargs)
