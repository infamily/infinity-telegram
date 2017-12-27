# coding: utf-8
from logging.config import dictConfig

from envparse import Env
from flask import Flask
from raven.contrib.flask import Sentry
from werkzeug.utils import import_string

env = Env()
settings_module = env('SETTINGS_MODULE', 'config.settings.local')


def create_app():
    appl = Flask(__name__)
    appl.config.from_object(settings_module)
    init_sentry(appl)
    update_logging(appl)
    register_extensions(appl)
    return appl


def register_extensions(appl):
    for path in appl.config.get('EXTENSIONS', []):
        cls = import_string(path)
        extension = cls()
        extension.init_app(appl)


def init_sentry(appl):
    dsn = appl.config.get('SENTRY_DSN')
    if not dsn:
        return
    sentry = Sentry(dsn=dsn)
    sentry.init_app(appl)


def update_logging(appl):
    config = appl.config.get('LOGGING', {})
    if not config:
        return
    dictConfig(config)


app = create_app()
