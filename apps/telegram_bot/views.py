# coding: utf-8
import json
import logging

from flask import Blueprint, request, current_app, jsonify


blueprint = Blueprint(__name__, __name__)
logger = logging.getLogger(__name__)


@blueprint.route('/webhook', methods=['POST'])
def webhook():
    """Handles webhook request"""
    payload = request.get_json()
    logger.debug('Request: {}'.format(json.dumps(payload)))
    telegram_bot = current_app.extensions['telegram_bot']
    response = telegram_bot.bot.webhook_handler(payload)
    logger.debug('Response: {}'.format(json.dumps(response)))
    return jsonify(response)
