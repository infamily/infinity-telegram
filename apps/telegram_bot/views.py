# coding: utf-8
import json
import logging

from flask import Blueprint, request, current_app, jsonify, make_response
from .base import get_telegram_ext

blueprint = Blueprint(__name__, __name__)
logger = logging.getLogger(__name__)


@blueprint.route('/webhook', methods=['POST'])
def webhook():
    """Handles webhook request"""
    payload = request.get_json()
    logger.debug('Request: {}'.format(json.dumps(payload)))
    telegram_ext = get_telegram_ext()
    telegram_ext.dispatcher.process_update(payload)
    return '', 202
