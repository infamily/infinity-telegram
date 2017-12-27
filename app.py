# coding: utf-8
import logging
from logging.config import dictConfig

import os
from envparse import Env
from flask import Flask
from raven.contrib.flask import Sentry
from werkzeug.utils import import_string


logger = logging.getLogger(__name__)
env = Env()
settings_module = env('SETTINGS_MODULE', 'config.settings.local')


def create_app():
    appl = Flask(__name__)
    appl.config.from_object(settings_module)
    update_logging(appl)
    init_sentry(appl)
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

    try:
        logging_level = int(appl.config.get('SENTRY_LOGGING_LEVEL'))
    except ValueError:
        logging_level = logging.ERROR

    if not dsn:
        return

    sentry = Sentry(dsn=dsn)
    sentry.init_app(app=appl, logging=True, level=logging_level)


def update_logging(appl):
    config = appl.config.get('LOGGING', {})
    if not config:
        return
    dictConfig(config)


app = create_app()
