# coding: utf-8
from django.db import models
from django.utils.translation import gettext
from schematics import Model as BaseModel
from schematics.types import IntType, URLType

from inftybot.core.models import StringType

_ = gettext


class Type_(BaseModel):
    """Type meta model"""

    class Meta:
        plural = 'types'

    id = IntType(required=False)
    url = URLType(required=False)
    name = StringType(required=True)
    definition = StringType(required=False)

    def __str__(self):
        return self.name


class Type(models.Model):
    class Meta:
        managed = False
        verbose_name = 'Type'
        verbose_name_plural = 'Types'

    url = models.URLField(verbose_name='URL')
    name = models.CharField(max_length=100, verbose_name=_('Name'))
    definition = models.CharField(max_length=100, verbose_name=_('Definition'))
