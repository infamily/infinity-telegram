# coding: utf-8
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils.translation import gettext as _


class Topic(models.Model):
    """Dummy topic model"""
    TYPE_NEED = 0
    TYPE_GOAL = 1
    TYPE_IDEA = 2
    TYPE_PLAN = 3
    TYPE_STEP = 4
    TYPE_TASK = 5

    TYPE_CHOICES = (
        (TYPE_NEED, 'Need'),
        (TYPE_GOAL, 'Goal'),
        (TYPE_IDEA, 'Idea'),
        (TYPE_PLAN, 'Plan'),
        (TYPE_STEP, 'Step'),
        (TYPE_TASK, 'Task')
    )

    class Meta:
        managed = False
        verbose_name_plural = 'Topics'

    type = models.SmallIntegerField(verbose_name=_('Type'), choices=TYPE_CHOICES)
    title = models.CharField(verbose_name=_('Title'), max_length=200)
    body = models.TextField(verbose_name=_('Body'))
    categories_names = ArrayField(
        models.CharField(max_length=100), verbose_name=_('Categories (names)'), blank=True, null=True, default=[])
    url = models.URLField(verbose_name=_('URL'), null=True, blank=True)
    parents = ArrayField(models.CharField(max_length=100), verbose_name=_('Parents'), blank=True, default=[])

    def __str__(self):
        topic_type = self.get_type_display() or '<no type>'
        topic_title = self.title or '<no title>'
        topic_str = "{}: {}".format(topic_type, topic_title)

        if not self.id:
            topic_str = "{} (draft)".format(topic_str)

        return topic_str
