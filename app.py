# coding: utf-8
import logging
from logging.config import dictConfig

import raven.base
from envparse import Env
from flask import Flask
from raven.contrib.flask import Sentry
from raven.transport import RequestsHTTPTransport
from werkzeug.utils import import_string

logger = logging.getLogger(__name__)
env = Env()
settings_module = env('SETTINGS_MODULE', 'config.settings.local')


def create_app():
    app = Flask(__name__)
    app.config.from_object(settings_module)
    update_logging(app)
    init_sentry(app)
    register_extensions(app)
    return app


def register_extensions(app):
    for path in app.config.get('EXTENSIONS', []):
        cls = import_string(path)
        extension = cls()
        extension.init_app(app)


def init_sentry(app):
    dsn = app.config.get('SENTRY_DSN')

    if not dsn:
        return

    try:
        logging_level = int(app.config.get('SENTRY_LOGGING_LEVEL'))
    except ValueError:
        logging_level = logging.ERROR

    client = raven.base.Client(dsn=dsn, transport=RequestsHTTPTransport, **{
        'include_paths': {'app'}
    })

    sentry = Sentry(dsn=dsn, client=client)
    sentry.init_app(app=app, logging=True, level=logging_level)


def update_logging(app):
    config = app.config.get('LOGGING', {})
    if not config:
        return
    dictConfig(config)


appl = create_app()
