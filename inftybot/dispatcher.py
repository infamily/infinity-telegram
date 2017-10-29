# coding: utf-8
import telegram
import telegram.ext


class Dispatcher(telegram.ext.Dispatcher):
    """
    Telegram event (update) Dispatcher that converts data
    from dict to ```telegram.Update``` object before ```process_update```
    """
    def process_update(self, update):
        if isinstance(update, dict):
            update = telegram.Update.de_json(update, self.bot)
        return super(Dispatcher, self).process_update(update)
