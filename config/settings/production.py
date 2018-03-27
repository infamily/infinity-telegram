# coding: utf-8

from config.settings.base import *

assert BASE_DIR

ALLOWED_HOSTS = [os.environ('LAMBDA_HOSTNAME')]

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
        'infinity': {
            'handlers': ['default'],
            'level': 'WARNING',
            'propagate': True
        },
        'tasks': {
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

RAVEN_CONFIG = {
    'dsn': 'https://de11ec10e94b44149a485c2e64348fd7:2737d16b26c445d5acee77ba89b168f3@sentry.io/270033',
    # If you are using git, you can also automatically configure the
    # release based on the git info.
    # 'release': raven.fetch_git_sha(BASE_DIR),
}
