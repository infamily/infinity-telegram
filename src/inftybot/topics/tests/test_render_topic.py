# coding: utf-8
from django.test import TestCase

from inftybot.topics.models import Topic
from inftybot.topics.utils import render_topic


class RenderLangsplitTestCase(TestCase):
    def test_default_language_renders_ok(self):
        title = ".:en:Title"
        body = """.:en
        body
        """

        instance = Topic(title=title, body=body)
        rendered = render_topic(instance)
        self.assertNotIn('.:en', rendered)
