# coding: utf-8
from schematics import Model as BaseModel
from schematics.types import IntType, URLType

from inftybot.core.models import StringType


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
