# coding: utf-8
import logging
from functools import wraps

from django.utils.module_loading import import_string

from inftybot.config import TELEGRAM_BOT_TOKEN
from inftybot.core.factory import create_bot

logger = logging.getLogger(__name__)


def task(func):
    """Decorator provides configured bot object to the task function"""
    bot = create_bot(token=TELEGRAM_BOT_TOKEN)

    @wraps(func)
    def wrapper(*args, **kwargs):
        logger.debug('Run task {}, args: {}, kwargs: {}'.format(func, args, kwargs))
        result = func(bot, **kwargs)
        logger.debug('Task complete, result: {}'.format(result))
        return result

    return wrapper


def run_with_django(event, context):
    """
    Run some function as AWS lambda event handler using Django
    """
    # setup django
    import django
    django.setup()

    # get function name from event kwargs
    kwargs = event.get('kwargs', {})
    func_str = kwargs.get('function')
    func_obj = import_string(func_str)

    # call function with event & context kwargs
    return func_obj(event=event, context=context)
