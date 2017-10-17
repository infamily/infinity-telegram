# coding: utf-8
from envparse import Env
from flask import Flask
from werkzeug.utils import import_string

env = Env()
settings_module = env('SETTINGS_MODULE', 'config.settings.local')


def create_app():
    appl = Flask(__name__)
    appl.config.from_object(settings_module)
    register_extensions(appl)
    return appl


def register_extensions(appl):
    for path in appl.config.get('EXTENSIONS', []):
        cls = import_string(path)
        extension = cls()
        extension.init_app(appl)


app = create_app()
