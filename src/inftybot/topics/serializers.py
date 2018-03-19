# coding: utf-8
from rest_framework import serializers

from inftybot.topics import models


class TopicSerializer(serializers.ModelSerializer):
    categories_str = serializers.ListField(child=serializers.CharField(), source='categories_names', default=[])

    class Meta:
        model = models.Topic
        fields = '__all__'
