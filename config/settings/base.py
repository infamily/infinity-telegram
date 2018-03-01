# coding: utf-
import logging
import os


BASE_DIR = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__), os.pardir, os.pardir
    )
)


DEBUG = False
SECRET_KEY = None
TESTING = False


EXTENSIONS = [
    'inftybot.contrib.flask.base.TelegramBot',
]


TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '')
TELEGRAM_BOT_FACTORY = os.environ.get('TELEGRAM_BOT_FACTORY', 'inftybot.factory.create_bot')
TELEGRAM_BOT_FACTORY_PARAMS = os.environ.get('TELEGRAM_BOT_FACTORY_PARAMS', {
    'token': TELEGRAM_BOT_TOKEN,

})


TELEGRAM_BOT_DISPATCHER_FACTORY = os.environ.get('TELEGRAM_BOT_DISPATCHER_FACTORY', 'inftybot.factory.create_dispatcher')
TELEGRAM_BOT_DISPATCHER_FACTORY_PARAMS = os.environ.get('TELEGRAM_BOT_DISPATCHER_FACTORY_PARAMS', {
    'class': 'inftybot.dispatcher.DynamoDispatcher',
    'workers': 1,  # because AWS Lambda is stateless
})

SENTRY_DSN = os.environ.get('SENTRY_DSN', None)
SENTRY_LOGGING_LEVEL = os.environ.get('SENTRY_LOGGING_LEVEL', logging.ERROR)
