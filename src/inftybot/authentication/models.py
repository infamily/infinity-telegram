# coding: utf-8
import datetime

from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.db.transaction import atomic
from django.utils.translation import gettext_lazy
from schematics.types import EmailType

from inftybot.core.models import Model, StringType

_ = gettext_lazy


class User(Model):
    email = EmailType(required=True)
    token = StringType(required=False)

    def __str__(self):
        return '<User: {}>'.format(self.email)


class ChatUserQuerySet(models.QuerySet):
    @atomic
    def create(self, **kwargs):
        instance = super(ChatUserQuerySet, self).create(**kwargs)
        instance.ensure_session()
        return instance


class ChatUserManager(models.Manager):
    pass


class ChatUser(models.Model):
    """Chat user model"""
    objects = ChatUserManager.from_queryset(ChatUserQuerySet)()

    username = models.CharField(max_length=150, verbose_name=_('Username'))
    email = models.EmailField(verbose_name=_('Email'))
    user = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, verbose_name=_('User reference'))

    def ensure_session(self):
        try:
            return self.session
        except Session.DoesNotExist:
            return Session.objects.create(user=self, session_key=self.id)


class Session(models.Model):
    """Chat user session"""
    user = models.OneToOneField(
        'authentication.ChatUser', models.CASCADE, verbose_name=_('User reference'), blank=True, null=True)
    session_key = models.CharField(max_length=40, verbose_name=_('Session key (chat user_id, e.g.)'))
    session_data = JSONField(verbose_name=_('Session data'), blank=True, null=False, default={})
    expire_date = models.DateTimeField(verbose_name=_('Session expires at'), blank=True, null=False)

    def save(self, *args, **kwargs):
        if not self.expire_date:
            # session never expires by default
            self.expire_date = datetime.datetime(2099, 12, 31)
        return super(Session, self).save()
