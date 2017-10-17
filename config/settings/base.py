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
    'apps.telegram_bot.base.TelegramBot',
]


TELEGRAM_BOT_TOKEN = env('TELEGRAM_BOT_TOKEN', '')
TELEGRAM_BOT_FACTORY = env('TELEGRAM_BOT_FACTORY', 'inftybot.factory.create_bot')
TELEGRAM_BOT_FACTORY_PARAMS = env('TELEGRAM_BOT_FACTORY_PARAMS', {
    'token': TELEGRAM_BOT_TOKEN
})
