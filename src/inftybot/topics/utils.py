# coding: utf-8
from inftybot.templating import render_template


def render_topic(topic):
    return render_template('topics/topic.md', topic.to_native())
