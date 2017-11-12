# coding: utf-8
import json
from schematics.models import Model as BaseModel
from schematics.types import IntType, StringType, URLType, ListType, EmailType


class Model(BaseModel):
    """Simple data model"""
    pass


class Topic(Model):
    pk = IntType(required=False)
    type = IntType(required=True)
    title = StringType(required=True, min_length=1)
    body = StringType(required=True, min_length=1)
    url = URLType(required=False)
    parents = ListType(IntType, required=True, default=[])


class User(Model):
    email = EmailType(required=True)
    token = StringType(required=False)
