# coding: utf-8
from django.template.loader import render_to_string


def render_topic(instance):
    return render_to_string('topics/topic.md', context={'object': instance})
