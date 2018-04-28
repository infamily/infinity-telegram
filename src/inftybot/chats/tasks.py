# coding: utf-8
import logging

from django.conf import settings
from langsplit import splitter
from telegram import ParseMode

from infinity.api.base import create_api_client
from inftybot.chats.models import Chat
from inftybot.topics.models import Topic
from inftybot.topics.serializers import TopicSerializer
from inftybot.topics.utils import render_topic
from tasks.base import task

api = create_api_client()
logger = logging.getLogger(__name__)


def _notify(bot, instance, chat_id):
    message = render_topic(instance)
    bot.send_message(chat_id, message, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)


def _notify_general_channels(bot, instance):
    general_chat_id = settings.GENERAL_CHATS[instance.type]

    if general_chat_id:
        _notify(bot, instance, general_chat_id)


def _notify_subscribed_chats(bot, instance, queryset):
    for chat in queryset.iterator():
        _notify(bot, instance, chat.id)


def _prepare_categories(instance):
    categories = []
    splitted = [splitter.split(value) for value in instance.categories_names]
    for value in splitted:
        categories.extend(value.values())
    return categories

    
@task
def notify_about_new_topic(bot, **kwargs):
    """
    Event handler for "new topic created" event.
    Sends notifications to subscribers
    """

    logger.debug("Run `notify_subscribers_about_new_topic` with {}".format(kwargs))

    pk = kwargs.get('event', {}).get('topic_id')

    if not pk:
        return

    logger.debug("Trying to fetch topic {} from API".format(pk))

    data = api.topics(pk).get()
    serializer = TopicSerializer(data=data)

    if not serializer.is_valid():
        logger.warning("Topic is not valid:\n{}\nSkipping...".format(serializer.errors))
        return

    instance = Topic(**serializer.validated_data)

    logger.debug("Notifying in existing general chats...")
    _notify_general_channels(bot, instance)

    categories = _prepare_categories(instance)

    if not categories:
        logger.debug("No topic categories\nSkipping...")
        return

    chats_queryset = Chat.objects.by_categories(categories).distinct().all()

    if not chats_queryset.exists():
        logger.debug("No chats subscribed to {}".format(categories))

    _notify_subscribed_chats(bot, instance, chats_queryset)
    
    return True
