# coding: utf-8
from rest_framework import serializers

from inftybot.topics import models


class TopicSerializer(serializers.ModelSerializer):
    """Seralizer for data fetched from the API (create instances, etc.)"""
    id = serializers.IntegerField(
        required=False, default=None, allow_null=True)
    type = serializers.ChoiceField(
        choices=models.Topic.TYPE_CHOICES, required=False, default=models.Topic.TYPE_NEED, allow_null=True)
    title = serializers.CharField(required=False, default=None, allow_null=True, allow_blank=True)
    body = serializers.CharField(required=False, default=None, allow_null=True, allow_blank=True)
    categories_names = serializers.ListField(
        child=serializers.CharField(), default=[])  # NOQA
    url = serializers.URLField(required=False, default=None, allow_null=True)
    parents = serializers.ListField(child=serializers.CharField(), default=[])

    class Meta:
        model = models.Topic
        fields = ('id', 'type', 'title', 'body', 'categories_names', 'categories_str', 'url', 'parents')
