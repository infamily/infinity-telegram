# coding: utf-8
from urllib.parse import urlparse

from django.template.loader import render_to_string

from inftybot import config


def get_topic_id(topic_url):
    try:
        return int(topic_url.strip('/').rsplit('/', 1)[-1])
    except (AttributeError, IndexError, TypeError):
        return None


def get_topic_client_url(instance):
    template = config.TOPIC_URL_TEMPLATE
    url_object = urlparse(config.INFTY_API_URL)
    topic_id = instance.get_topic_id()
    context = {
        'INFTY_API_URL': url_object.netloc,
        'TOPIC_ID': topic_id,
    }
    return template.format(**context)


def render_topic(instance):
    return render_to_string('topics/topic.md', context={'object': instance})
