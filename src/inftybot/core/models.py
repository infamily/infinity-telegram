# coding: utf-8
from schematics import Model as BaseModel
from schematics.exceptions import ValidationError
from schematics.types import Serializable, StringType as BaseStringType


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
