# coding: utf-8
from schematics.models import Model as BaseModel
from schematics.types import StringType as BaseStringType, IntType, URLType, ListType, EmailType
from schematics.exceptions import ValidationError


class Model(BaseModel):
    """Simple data model"""
    @classmethod
    def from_native(cls, data):
        instance = cls()
        for key, value in data.items():
            if hasattr(cls, key):
                setattr(instance, key, value)
        return instance


class StringType(BaseStringType):
    def validate_string_not_empty(self, value):
        if not len(value):
            raise ValidationError("Value of {} field shouldn't be an empty string".format(self.name))
        return value


class Topic(Model):
    id = IntType(required=False)
    type = IntType(required=True)
    title = StringType(required=True, min_length=1)
    body = StringType(required=True, min_length=1)
    url = URLType(required=False)
    parents = ListType(StringType, required=True, default=[])


class User(Model):
    email = EmailType(required=True)
    token = StringType(required=False)
