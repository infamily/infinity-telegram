# coding: utf-8
import click
from flask import current_app

from inftybot import storage


@current_app.cli.command()
def create_tables():
    """Create all tables in DynamoDB"""
    registry = storage.storage_registry
    storage.create_tables(registry)


@current_app.cli.command()
def drop_tables():
    """Drop all tables in DynamoDB"""
    # todo make it confirmable
    registry = storage.storage_registry
    storage.drop_tables(registry)


@current_app.cli.command()
@click.argument('url')
def set_webhook(url):
    """Sets telegram bot webhook from ```url```"""
    telegram_bot = current_app.extensions['telegram_bot']
    telegram_bot.bot.set_webhook(url)
    print(telegram_bot.bot.get_webhook_info())


@current_app.cli.command()
def webhook_info():
    """Prints telegram bot webhook info"""
    telegram_bot = current_app.extensions['telegram_bot']
    print(telegram_bot.bot.get_webhook_info())
