# coding: utf-8
from inftybot.intents import constants


def render_topic(topic):
    template = "`{type}:` *{topic.title}*\n\n{topic.body}\n\n*URL:* {topic.url}\n" \
               "_Reply to this message to post a comment on Infinity._"

    return template.format(
        type=constants.TOPIC_TYPE_CHOICES.get(topic.type),
        topic=topic,
    )
