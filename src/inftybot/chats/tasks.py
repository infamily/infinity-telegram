# coding: utf-8
import logging

from langsplit import splitter
from telegram import ParseMode

from infinity.api.base import create_api_client
from inftybot.chats.models import Chat
from inftybot.topics.models import Topic
from inftybot.topics.serializers import TopicSerializer
from inftybot.topics.utils import render_topic
from tasks.base import task

from django.conf import settings

api = create_api_client()
logger = logging.getLogger(__name__)


@task
def notify_about_new_topic(bot, **kwargs):
    """
    Event handler for "new topic created" event.
    Sends notifications to subscribers
    """

    logger.error("Run `notify_subscribers_about_new_topic` with {}".format(kwargs))

    pk = kwargs.get('event', {}).get('topic_id')

    if not pk:
        return

    logger.error("Trying to fetch topic {} from API".format(pk))

    data = api.topics(pk).get()
    serializer = TopicSerializer(data=data)

    if not serializer.is_valid():
        logger.error("Topic is not valid:\n{}\nSkipping...".format(serializer.errors))
        return

    categories = []
    instance = Topic(**serializer.validated_data)
    splitted = [splitter.split(value) for value in instance.categories_names]

    for value in splitted:
        categories.extend(value.values())

    logger.error("Notifying in existing general chats...")
    general_chat_id = settings.GENERAL_CHATS[instance.type]

    if general_chat_id:
        message = render_topic(instance)
        bot.send_message(general_chat_id, message, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)

    if not categories:
        logger.error("No topic categories\nSkipping...")
        return

    chats_queryset = Chat.objects.by_categories(categories).distinct().all()

    if not chats_queryset.exists():
        logger.error("No chats subscribed to {}".format(categories))

    for chat in chats_queryset.iterator():
        message = render_topic(instance)
        bot.send_message(chat.id, message, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)


    return True
