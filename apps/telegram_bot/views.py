# coding: utf-8
from flask import Blueprint, request, current_app, jsonify

blueprint = Blueprint(__name__, __name__)


@blueprint.route('/webhook', methods=['POST'])
def webhook():
    """Handles webhook request"""
    payload = request.json
    telegram_bot = current_app.extensions['telegram_bot']
    response = telegram_bot.bot.webhook_handler(payload)
    return jsonify(response)
