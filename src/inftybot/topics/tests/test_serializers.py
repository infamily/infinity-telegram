# coding: utf-8
# flake8: noqa

from django.test import TestCase

from inftybot.topics.models import Topic
from inftybot.topics.serializers import TopicSerializer


class TopicSerializerTestCase(TestCase):
    def test_serializer_data_has_empty_default_categories_str_field(self):
        data = {
            'title': 'Test title',
            'body': 'Test body',
            'type': Topic.TYPE_NEED,
        }
        serializer = TopicSerializer(data=data)
        serializer.is_valid()
        self.assertEqual([], serializer.data['categories_str'])

    def test_serializer_data_has_categories_str_field(self):
        instance = Topic(categories_names=['test1', 'test2'])

        data = {
            'title': 'Test title',
            'body': 'Test body',
            'type': Topic.TYPE_NEED,
        }

        serializer = TopicSerializer(instance, data=data)
        serializer.is_valid()
        self.assertEqual(['test1', 'test2'], serializer.data['categories_str'])

    def test_id_field_in_validated_data(self):
        data = {
            'id': 1,
            'title': 'Test title',
            'body': 'Test body',
            'type': Topic.TYPE_NEED,
        }

        serializer = TopicSerializer(data=data)
        serializer.is_valid()
        self.assertEqual(1, serializer.validated_data['id'])

    def test_instance_passed_validated_data_ok(self):
        instance = Topic(**{'id': 1, 'title': 'Title'})
        serializer = TopicSerializer(instance)
        self.assertEqual(1, serializer.data['id'])
