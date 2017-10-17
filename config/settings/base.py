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
