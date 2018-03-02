# coding: utf-8
from django.core.management import BaseCommand

from inftybot.core.factory import create_bot


class Command(BaseCommand):
    help = 'Sets webhook url on the Telegram side'

    def add_arguments(self, parser):
        parser.add_argument('url', type=str)

    def handle(self, *args, **options):
        """Sets telegram bot webhook from ```url```"""
        telegram_bot = create_bot()
        telegram_bot.set_webhook(options['url'])
        print(telegram_bot.get_webhook_info())
