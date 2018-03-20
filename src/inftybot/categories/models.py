# coding: utf-8
from django.db import models
from django.utils.translation import gettext

_ = gettext


class Type(models.Model):
    class Meta:
        managed = False
        verbose_name = 'Type'
        verbose_name_plural = 'Types'

    url = models.URLField(verbose_name='URL')
    name = models.CharField(max_length=100, verbose_name=_('Name'))
    definition = models.CharField(max_length=100, verbose_name=_('Definition'))
