# coding: utf-8
from schematics.exceptions import ValidationError
from schematics.models import Model as BaseModel
from schematics.types import StringType as BaseStringType, IntType, URLType, ListType, EmailType, serializable, \
    Serializable

from inftybot import constants


def from_native(cls, data):
    """Create instance of cls poplated with data"""
    instance = cls()
    for key, value in data.items():
        try:
            field = getattr(cls, key)
        except AttributeError:
            continue
        if isinstance(field, Serializable):
            continue
        setattr(instance, key, value)
    return instance


class Model(BaseModel):
    """Simple data model"""
    class Meta:
        plural = None

    @classmethod
    def from_native(cls, data):
        return from_native(cls, data)


class StringType(BaseStringType):
    def validate_string_not_empty(self, value):
        if not len(value):
            raise ValidationError("Value of {} field shouldn't be an empty string".format(self.name))
        return value


class Type(BaseModel):
    """Type meta model"""
    class Meta:
        plural = 'types'

    id = IntType(required=False)
    url = URLType(required=False)
    name = StringType(required=True)
    definition = StringType(required=False)

    def __str__(self):
        return self.name


class Topic(Model):
    class Meta:
        plural = 'topics'

    id = IntType(required=False)
    type = IntType(required=True)
    title = StringType(required=True, min_length=1)
    body = StringType(required=True, min_length=1)
    categories = ListType(StringType, default=[], required=False)
    url = URLType(required=False)
    parents = ListType(StringType, required=True, default=[])

    @serializable
    def type_str(self):
        return constants.TOPIC_TYPE_CHOICES.get(self.type)

    def __str__(self):
        topic_type = constants.TOPIC_TYPE_CHOICES.get(self.type, '<no type>')

        topic_str = "{}: {}".format(
            topic_type, self.title or '<no title>'
        )
        if not self.id:
            topic_str = "{} (draft)".format(topic_str)

        return topic_str


class User(Model):
    email = EmailType(required=True)
    token = StringType(required=False)

    def __str__(self):
        return '<User: {}>'.format(self.email)
