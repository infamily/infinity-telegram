# coding: utf-8
from django.db import models
from django.utils.translation import gettext

from inftybot.categories.constants import MAX_CATEGORY_NAME_LENGTH

_ = gettext


class Type(models.Model):
    """
    Model for Infty API "Type" entity that represents a Category (when proper type is set)
    """
    class Meta:
        managed = False
        verbose_name = 'Type'
        verbose_name_plural = 'Types'  # used to generate API endpoint URL (see `infinity.api.utils.get_model_resource`)

    url = models.URLField(verbose_name='URL')
    name = models.CharField(max_length=MAX_CATEGORY_NAME_LENGTH, verbose_name=_('Name'))
    definition = models.CharField(max_length=MAX_CATEGORY_NAME_LENGTH, verbose_name=_('Definition'))
