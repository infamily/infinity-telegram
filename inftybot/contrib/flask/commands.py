# coding: utf-8
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
