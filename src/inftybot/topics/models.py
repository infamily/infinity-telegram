# coding: utf-8
from schematics.types import IntType, ListType, URLType, serializable

from inftybot.core.models import Model, StringType
from inftybot.topics import constants


class Topic(Model):
    class Meta:
        plural = 'topics'

    id = IntType(required=False)
    type = IntType(required=True)
    title = StringType(required=True, min_length=1)
    body = StringType(required=True, min_length=1)
    categories_names = ListType(StringType, required=False, default=[])
    url = URLType(required=False)
    parents = ListType(StringType, required=True, default=[])

    @serializable
    def categories_str(self):
        """Used as data field when send to the API"""
        return self.categories_names

    @serializable
    def type_str(self):
        return constants.TOPIC_TYPE_CHOICES.get(self.type)

    def __str__(self):
        topic_type = constants.TOPIC_TYPE_CHOICES.get(self.type, '<no type>')

        topic_str = "{}: {}".format(
            topic_type, self.title or '<no title>'
        )
        if not self.id:
            topic_str = "{} (draft)".format(topic_str)

        return topic_str
