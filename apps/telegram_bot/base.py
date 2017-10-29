# coding: utf-8
from flask import current_app
from werkzeug.utils import import_string


EXTENSION_NAME = 'telegram_bot'


def create_bot(app):
    """Create bot instance using factory"""
    factory = import_string(app.config.get('TELEGRAM_BOT_FACTORY'))
    params = app.config.get('TELEGRAM_BOT_FACTORY_PARAMS')
    return factory(**params)


def create_dispatcher(app, bot):
    """
    Create TG event dispatcher instance
    :param app:
    :param bot: bot instance
    :return:
    """
    factory = import_string(app.config.get('TELEGRAM_BOT_DISPATCHER_FACTORY'))
    params = app.config.get('TELEGRAM_BOT_DISPATCHER_FACTORY_PARAMS')
    return factory(bot, **params)


def register_commands(app):
    """Registers shell commands"""
    with app.app_context():
        from . import commands
        assert commands


def register_blueprint(app):
    """Registers view blueprints"""
    with app.app_context():
        from .views import blueprint
        app.register_blueprint(blueprint, url_prefix='/telegram')


def get_telegram_ext():
    return current_app.extensions[EXTENSION_NAME]


class TelegramBot(object):
    """Pluggable flask app for handling telegram bot intents via webhook"""
    def __init__(self, app=None):
        self.bot = None
        self.dispatcher = None

        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        self.bot = create_bot(app)
        self.dispatcher = create_dispatcher(app, self.bot)

        register_commands(app)
        register_blueprint(app)
        app.extensions[EXTENSION_NAME] = self
