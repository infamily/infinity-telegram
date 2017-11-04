# coding: utf-8
import json
from schematics.models import Model as BaseModel
from schematics.types import IntType, StringType, URLType, ListType, EmailType


class Model(BaseModel):
    """Simple data model"""
    pass


class Topic(Model):
    type = IntType(required=True)
    title = StringType(required=True)
    body = StringType(required=True)
    url = URLType(required=False)
    parents = ListType(IntType, required=False)


class User(Model):
    email = EmailType(required=True)
    token = StringType(required=False)
