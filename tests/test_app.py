# coding: utf-8
from flask_testing import TestCase

from app import create_app


class AppInstantiationTestCase(TestCase):
    def create_app(self):
        app = create_app()
        return app

    def test_app_initialized(self):
        self.assertTrue(self.app.extensions)
