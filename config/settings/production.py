# coding: utf-8

DEBUG = False
TESTING = False

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
            'level': 'WARNING',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'inftybot': {
            'handlers': ['default'],
            'level': 'WARNING',
            'propagate': True
        },
        'telegram': {
            'handlers': ['default'],
            'level': 'WARNING',
            'propagate': True
        }
    }
}
