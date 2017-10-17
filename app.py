# coding: utf-8
from envparse import Env
from flask import Flask

env = Env()
settings_module = env('SETTINGS_MODULE', 'config.settings.local')

app = Flask(__name__)
app.config.from_object(settings_module)
