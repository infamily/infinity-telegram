# coding: utf-
import os

from envparse import Env

BASE_DIR = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__), os.pardir, os.pardir
    )
)


env = Env()
env.read_envfile(os.path.join(BASE_DIR, '.env'))


DEBUG = False
SECRET_KEY = None
TESTING = False


EXTENSIONS = [
    'inftybot.contrib.flask.base.TelegramBot',
]


TELEGRAM_BOT_TOKEN = env('TELEGRAM_BOT_TOKEN', '')
TELEGRAM_BOT_FACTORY = env('TELEGRAM_BOT_FACTORY', 'inftybot.factory.create_bot')
TELEGRAM_BOT_FACTORY_PARAMS = env('TELEGRAM_BOT_FACTORY_PARAMS', {
    'token': TELEGRAM_BOT_TOKEN,

})


TELEGRAM_BOT_DISPATCHER_FACTORY = env('TELEGRAM_BOT_DISPATCHER_FACTORY', 'inftybot.factory.create_dispatcher')
TELEGRAM_BOT_DISPATCHER_FACTORY_PARAMS = env('TELEGRAM_BOT_DISPATCHER_FACTORY_PARAMS', {
    'class': 'inftybot.dispatcher.DynamoDispatcher',
    'workers': 1,  # because AWS Lambda is stateless
})


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
            'level': 'INFO',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        '': {
            'handlers': ['default'],
            'level': 'INFO',
            'propagate': True
        }
    }
}
