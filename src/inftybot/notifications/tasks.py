# coding: utf-8
import logging

from langsplit import splitter

from infinity.api.base import create_api_client
from inftybot.categories.models import CategoriesSet
from inftybot.chats.models import Chat
from inftybot.tasks.base import task
from inftybot.topics.models import Topic
from inftybot.topics.serializers import TopicSerializer

api = create_api_client()
logger = logging.getLogger(__name__)


@task
def notify_subscribers_about_new_topic(bot, **kwargs):
    """
    Event handler for "new topic created" event.
    Sends notifications to subscribers
    """

    # Entities: Chat, Topic, Category

    # *. Fetch topic data from API
    # *. Instantiate it ?
    # *. Retrievee its categories
    # *. Get chats that subscribed to theese categories
    # *. Send message to every chat from last point
    logging.debug("Run `notify_subscribers_about_new_topic` with kwargs {}".format(kwargs))

    pk = kwargs.get('event', {}).get('topic_id')

    if not pk:
        return

    data = api.topics(pk).get()
    serializer = TopicSerializer(data=data)

    if not serializer.is_valid():
        return

    categories = []
    instance = Topic(**serializer.validated_data)
    splitted = [splitter.split(value) for value in instance.categories_names]

    for value in splitted:
        categories.extend(value.values())

    if not categories:
        return

    categories_queryset = CategoriesSet.objects.by_categories(categories).values('chat_id')
    chats_queryset = Chat.objects.filter(id__in=categories_queryset).all()

    for chat in chats_queryset.iterator():
        bot.send_message(chat.id, 'Hello')
