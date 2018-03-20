# coding: utf-8
from rest_framework import serializers

from inftybot.topics import models


class TopicSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False, default=None, allow_null=True)
    categories_str = serializers.ListField(child=serializers.CharField(), source='categories_names', default=[])  # NOQA

    class Meta:
        model = models.Topic
        fields = ('id', 'type', 'title', 'body', 'categories_names', 'categories_str', 'url', 'parents')
