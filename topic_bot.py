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
from topic import Topic
from constants import SERVER_PATH

# Enable logging
logging.basicConfig(format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level = logging.INFO)

logger = logging.getLogger(__name__)

# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.

TOPIC_TITLE, TOPIC_BODY, TOPIC_PARENTS = range(3)
token = '6b7b4bf980cc3fdcfce2ae44939693dc8f023018'
data = {}

# test
user = User('longx695@gmail.com')
user.token = token
data['user'] = user

def topic_new(bot, update):
    if ('user' not in data or token is ''):
        update.message.reply_text('You have to login to create a topic. Please use /register to login')
        return ConversationHandler.END
    new_topic = Topic()
    data['new_topic'] = new_topic
    keyboard = [
        [
            InlineKeyboardButton("Need", callback_data = '0'),
            InlineKeyboardButton("Goal", callback_data = '1'),
            InlineKeyboardButton("Idea", callback_data = '2')
        ],
        [
            InlineKeyboardButton("Plan", callback_data = '3'),
            InlineKeyboardButton("Task", callback_data = '4')
        ]
    ]
    update.message.reply_text('Please choose:',
                              reply_markup = InlineKeyboardMarkup(keyboard))
    return TOPIC_TITLE

def topic_callback(bot, update):
    query = update.callback_query
    message = query.message
    chat_id = message.chat_id
    message_id = message.message_id
    type = int(query.data)
    bot.delete_message(chat_id = chat_id,
                       message_id = message_id)
    if type < 5:
        new_topic = data['new_topic']
        new_topic.type = type
        types = ['Need', 'Goal', 'Idea', 'Plan', 'Task']
        bot.send_message(chat_id = chat_id,
                         text = "Type: %s\nPlease input Title." % types[type])
    elif type is 6:
        bot.send_message(chat_id = chat_id,
                         text = "Please type /done to finish")
    else:
        print ('parents')

def topic_title(bot, update):
    new_topic = data['new_topic']
    if new_topic.type is -1:
        return
    title = update.message.text
    new_topic.title = title
    update.message.reply_text('Title: %s\nPlease input body.' % title)
    return TOPIC_BODY

def topic_body(bot, update):
    body = update.message.text
    new_topic = data['new_topic']
    new_topic.body = body
    keyboard = [
        [InlineKeyboardButton("Parents", switch_inline_query_current_chat = "parents")],
        [InlineKeyboardButton("Done", callback_data = "6")]
    ]
    bot.send_message(chat_id = update.message.chat_id,
                     text = 'Body: %s\nSelect Parents' % body,
                     reply_markup = InlineKeyboardMarkup(keyboard))
    data['topics'] = Topic.topics(token)
    return TOPIC_PARENTS

def topic_parents(bot, update):
    parent = update.message.text
    topics = data['topics']
    new_topic = data['new_topic']
    if parent in new_topic.parents:
        return
    if parent in topics:
        new_topic.parents.append(parent)

def topic_list(bot, update):
    if ('user' not in data or token is ''):
        update.message.reply_text('You have to login to create a topic. Please use /register to login')
        return
    update.message.reply_text('topic_list')
    print ('topic_list')

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

def topic_done(bot, update):
    new_topic = data['new_topic']
    new_topic.create(token)
    bot.send_message(chat_id = update.message.chat_id,
                     text = 'New topic created')
    return ConversationHandler.END

def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))

TOPIC_URL_PATTERN = '^(https://test.wfx.io/api/v1/topics/[0-9]+/)$'

def main():
    updater = Updater('421683175:AAErGVBS_Av0XD5dz-rWHBuZinPYDP0_wCg')
    dp = updater.dispatcher
    topics_handler = ConversationHandler(
        entry_points = [CommandHandler('newtopic', topic_new)],
        states = {
            TOPIC_TITLE: [MessageHandler(Filters.text, topic_title)],
            TOPIC_BODY: [MessageHandler(Filters.text, topic_body)],
            TOPIC_PARENTS: [RegexHandler(TOPIC_URL_PATTERN, topic_parents)],
        },
        fallbacks = [CommandHandler('done', topic_done)],
    )
    dp.add_handler(topics_handler)
    topics_handler = ConversationHandler(
        entry_points = [CommandHandler('newtopic', topic_new)],
        states = {
            TOPIC_TITLE: [MessageHandler(Filters.text, topic_title)],
            TOPIC_BODY: [MessageHandler(Filters.text, topic_body)],
            TOPIC_PARENTS: [RegexHandler(TOPIC_URL_PATTERN, topic_parents)],
        },
        fallbacks = [CommandHandler('done', topic_done)],
    )
    dp.add_handler(topics_handler)
    dp.add_handler(CallbackQueryHandler(topic_callback))
    dp.add_handler(InlineQueryHandler(inline_topic_query))
    dp.add_error_handler(error)
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()