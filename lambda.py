# coding: utf-8
import json
import logging

from inftybot.chats import tasks as chats_tasks

logger = logging.getLogger(__name__)
tasks = []


def notify_subscribers_about_new_topic(event, context):
    record = event['Records'][0]
    message = record['Sns']['Message']
    data = json.loads(message)
    return chats_tasks.notify_about_new_topic(event=data)
