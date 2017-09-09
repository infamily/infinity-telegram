#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Simple Bot to reply to Telegram messages
# This program is dedicated to the public domain under the CC0 license.
"""
This Bot uses the Updater class to handle the bot.

First, a few handler functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Basic Echobot example, repeats messages.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import sys
import logging
import re
import json

from uuid import uuid4

import telegram
from telegram import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton, InlineQueryResultArticle, InputTextMessageContent, ParseMode
from telegram.ext import Updater, Filters, CommandHandler, MessageHandler, ConversationHandler, CallbackQueryHandler, InlineQueryHandler, RegexHandler

from user import User
from comment import Comment
from topic import Topic
from constants import SERVER_PATH

# Enable logging
logging.basicConfig(format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level = logging.INFO)

logger = logging.getLogger(__name__)

# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.

COMMENT_TOPIC, COMMENT_TEXT, COMMENT_CH, COMMENT_AH = range(4)

token = '6b7b4bf980cc3fdcfce2ae44939693dc8f023018'
data = {}

user = User('longx695@gmail.com')
user.token = token
data['user'] = user

def comment_new(bot, update):
    if ('user' not in data or token is ''):
        update.message.reply_text('You have to login to create a topic. Please use /register to login')
        return ConversationHandler.END
    new_comment = Comment()
    data['new_comment'] = new_comment
    keyboard = [[InlineKeyboardButton("Select Topic", switch_inline_query_current_chat = 'topics')]]
    data['topics'] = Topic.topics(token)
    update.message.reply_text('Select Topic', reply_markup = InlineKeyboardMarkup(keyboard))
    return COMMENT_TOPIC

def comment_topic(bot, update):
    topic = update.message.text
    topics = data['topics']
    if topic in topic:
        new_comment = data['new_comment']
        new_comment.topic = topic
        update.message.reply_text('Please input text.')
        return COMMENT_TEXT

def comment_text(bot, update):
    new_comment = data['new_comment']
    text = update.message.text
    new_comment.text = text
    update.message.reply_text('Text: %s\nPlease input Claimed hours.' % text)
    return COMMENT_CH

def comment_ch(bot, update):
    new_comment = data['new_comment']
    ch = update.message.text
    new_comment.claimed_hours = ch
    update.message.reply_text('Claimed hours: %s\nPlease input Claimed hours.' % ch)
    return COMMENT_AH

def comment_ah(bot, update):
    new_comment = data['new_comment']
    ah = update.message.text
    new_comment.assumed_hours = ah
    new_comment.create(token)
    update.message.reply_text('Claimed hours: %s\nA new comment has been created.' % ah)
    return ConversationHandler.END

def inline_topic_query(bot, update):
    query = update.inline_query.query
    query = query.decode('utf-8')
    results = list()
    if query == 'parents':
        if 'topics' not in data:
            return
        if 'new_topic' not in data:
            return
        topics = data['topics']
        new_topic = data['new_topic']
        for topic in topics:
            if topic.url in new_topic.parents:
                continue
            else:
                results.append(InlineQueryResultArticle(id = uuid4(),
                                                        title = topic.title,
                                                        input_message_content = InputTextMessageContent(topic.url)))
        update.inline_query.answer(results)
    if query == 'topics':
        if 'topics' not in data:
            return
        topics = data['topics']
        for topic in topics:
            results.append(InlineQueryResultArticle(id = uuid4(),
                                                    title = topic.title,
                                                    input_message_content = InputTextMessageContent(topic.url)))
        update.inline_query.answer(results)

def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))

def main():
    # Create the EventHandler and pass it your bot's token.
    updater = Updater('421683175:AAErGVBS_Av0XD5dz-rWHBuZinPYDP0_wCg')

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    comment_handler = ConversationHandler(
        entry_points = [CommandHandler('newcomment', comment_new)],
        states = {
            COMMENT_TOPIC: [RegexHandler('^(https://test.wfx.io/api/v1/topics/[0-9]+/)$', comment_topic)],
            COMMENT_TEXT: [MessageHandler(Filters.text, comment_text)],
            COMMENT_CH: [MessageHandler(Filters.text, comment_ch)],
            COMMENT_AH: [MessageHandler(Filters.text, comment_ah)],
        },
        fallbacks = [CommandHandler('cancel', error)],
    )
    dp.add_handler(comment_handler)
    # dp.add_handler(CommandHandler('findtopic', topic_list)),
    dp.add_handler(InlineQueryHandler(inline_topic_query))

    # on noncommand i.e message - echo the message on Telegram

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()

if __name__ == '__main__':
    main()