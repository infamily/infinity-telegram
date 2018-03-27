# coding: utf-8
import json
import logging

from django.http import HttpResponse
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from inftybot.core import factory

logger = logging.getLogger(__name__)


@require_http_methods(["POST"])
@csrf_exempt
@xframe_options_exempt
def webhook(request):
    """Handles webhook request"""
    payload = json.loads(request.body)
    logger.debug('Request: {}'.format(json.dumps(payload)))
    bot = factory.create_bot()
    dispatcher = factory.create_dispatcher(bot)
    dispatcher.process_update(payload)
    return HttpResponse('', status=202)
