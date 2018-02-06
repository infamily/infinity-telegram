# coding: utf-8
import gettext

from telegram.ext import CommandHandler

from inftybot.api.utils import get_model_resource
from inftybot.intents import states
from inftybot.intents.base import BaseCommandIntent, AuthenticatedMixin
from inftybot.models import Type

_ = gettext.gettext


def render_category_list(response):
    values = sorted(['[{}]'.format(r['name']) for r in response])
    return " - ".join(values)


class ListCategoriesCommandIntent(AuthenticatedMixin, BaseCommandIntent):
    """List categories command"""

    @classmethod
    def get_handler(cls):
        return CommandHandler("listcategories", cls.as_callback(), pass_chat_data=True, pass_user_data=True)

    def handle(self, *args, **kwargs):
        category_resource = get_model_resource(self.api, Type)
        response = category_resource.get(**{'lang': 'en'})

        self.bot.send_message(
            chat_id=self.update.effective_chat.id,
            text=render_category_list(response),
        )

        return states.STATE_END
