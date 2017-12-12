# coding: utf-8
EXTENSION_NAME = 'inftybot'
# todo merge with apps.telegram_bot


class Inftybot(object):
    """Pluggable flask app for inftybot-specific utils"""
    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        register_commands(app)
        app.extensions[EXTENSION_NAME] = self


def register_commands(app):
    """Registers shell commands"""
    with app.app_context():
        from . import commands
        assert commands
