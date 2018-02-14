# coding: utf-8
from .base import *  # NOQA

DEBUG = True
TESTING = True


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
    },
    'handlers': {
        'default': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'telegram_bot': {
            'handlers': ['default'],
            'level': 'DEBUG',
            'propagate': True
        },
        'telegram': {
            'handlers': ['default'],
            'level': 'DEBUG',
            'propagate': True
        }
    }
}
