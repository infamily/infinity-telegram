# coding: utf-8
from inftybot.templating import render_template


def render_topic(topic):
    return render_template('topics/topic.md', topic.to_native())


def render_error_list(errors):
    message_list = []

    for field, messages in errors:
        for message in messages:
            message_list.append(
                "{}: {}".format(field, message)
            )

    return message_list


def render_model_errors(error):
    return render_error_list(error.messages.items())
