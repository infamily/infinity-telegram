# coding: utf-8
from schematics.types import EmailType

from inftybot.core.models import Model, StringType


class User(Model):
    email = EmailType(required=True)
    token = StringType(required=False)

    def __str__(self):
        return '<User: {}>'.format(self.email)
