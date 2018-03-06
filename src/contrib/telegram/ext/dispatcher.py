# coding: utf-8
import telegram.ext

from inftybot.core.utils import update_from_dict


class Dispatcher(telegram.ext.Dispatcher):
    """
    Telegram event (update) Dispatcher that converts data
    from dict to ```telegram.Update``` object before ```process_update```
    """

    def process_update(self, update):
        if isinstance(update, dict):
            update = update_from_dict(self.bot, update)
        return super(Dispatcher, self).process_update(update)
