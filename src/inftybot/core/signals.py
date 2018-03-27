# coding: utf-8
from django.dispatch import Signal

handle_success = Signal(providing_args=['return_value'])
