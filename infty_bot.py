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
import logging
import re
import json

from uuid import uuid4

import telegram
from telegram import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton, InlineQueryResultArticle, InputTextMessageContent, ParseMode
from telegram.ext import Updater, Filters, CommandHandler, MessageHandler, ConversationHandler, CallbackQueryHandler, InlineQueryHandler, RegexHandler

from user import User
from topic import Topic
from comment import Comment
from constants import SERVER_PATH

# Enable logging
logging.basicConfig(format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level = logging.INFO)

logger = logging.getLogger(__name__)

# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.

AUTH_EMAIL, AUTH_CAPTCHA, AUTH_PASSWORD = range(3)
TOPIC_TITLE, TOPIC_BODY, TOPIC_PARENTS = range(3)
COMMENT_TOPIC, COMMENT_TEXT, COMMENT_CH, COMMENT_AH = range(4)

token = '6b7b4bf980cc3fdcfce2ae44939693dc8f023018'
data = {}

# Test value
user = User('longx695@gmail.com')
user.token = token
data['user'] = user

EMAIL_PATTERN = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'

# user authentication
def auth_register(bot, update):
    update.message.reply_text('What\'s your e-mail?')
    return AUTH_EMAIL

def auth_email(bot, update):
    user_email = update.message.text
    if not re.match(EMAIL_PATTERN, user_email):
        update.message.reply_text('Please enter valid email')
        return AUTH_EMAIL
    bot.send_chat_action(chat_id = update.message.chat_id,
                         action = telegram.ChatAction.TYPING)
    user = User(user_email)
    captcha = user.get_captcha()
    data['user'] = user
    data['captcha'] = captcha
    bot.sendPhoto(chat_id = update.message.chat_id,
                  photo = SERVER_PATH + captcha['image_url'])
    update.message.reply_text('Please, solve the captcha.')
    return AUTH_CAPTCHA

def auth_captcha(bot, update):
    captcha_value = update.message.text
    if 'user' not in data or 'captcha' not in data:
        print ('captcha_error')
        return
    user = data['user']
    captcha = data['captcha']
    res = user.signup(captcha['key'], captcha_value)
    if res.status_code == 200:
        print res.text
        token = json.loads(res.text)['token']
        del data['captcha']
        data['token'] = token
        update.message.reply_text('Please input OTP password')
        return AUTH_PASSWORD
    else:
        captcha = json.loads(res.content)
        data['captcha'] = captcha
        bot.sendPhoto(chat_id = update.message.chat_id,
                      photo = SERVER_PATH + captcha['image_url'])
        update.message.reply_text('Please, solve the captcha.')
        return AUTH_CAPTCHA

def auth_password(bot, update):
    password = update.message.text
    if 'user' not in data or 'token' not in data:
        print ('password_error')
        return
    user = data['user']
    token = data['token']
    if user.login(token, password):
        update.message.reply_text('Login Successed')
        return ConversationHandler.END
    else:
        update.message.reply_text('Login Failed')

def user_logout(bot, update):
    if 'user' not in data or 'token' not in data:
        update.message.reply_text('You need to login in order to logout')
        return
    del data['user']
    del data['token']
    update.message.reply_text('Logged out!')
def user_status(bot, update):
    if 'user' not in data or 'token' not in data:
        update.message.reply_text('You are not logged in')
        return
    user = data['user']
    update.message.reply_text('(' + user.email + ') is logged in')

# topics
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
    update.message.reply_text('Please choose:', reply_markup = InlineKeyboardMarkup(keyboard))
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
    print (parent)
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

def topic_done(bot, update):
    new_topic = data['new_topic']
    new_topic.create(token)
    bot.send_message(chat_id = update.message.chat_id,
                     text = 'New topic created')
    return ConversationHandler.END

# comment
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
    # on different commands - answer in Telegram
    auth_handler = ConversationHandler(
        entry_points = [CommandHandler('register', auth_register)],
        states = {
            AUTH_EMAIL: [MessageHandler(Filters.text, auth_email)],
            AUTH_CAPTCHA: [MessageHandler(Filters.text, auth_captcha)],
            AUTH_PASSWORD: [MessageHandler(Filters.text, auth_password)]
        },
        fallbacks = [CommandHandler('cancel', error)]
    )
    dp.add_handler(auth_handler)
    dp.add_handler(CommandHandler("logout", user_logout))
    dp.add_handler(CommandHandler("status", user_status))
    topics_handler = ConversationHandler(
        entry_points = [CommandHandler('newtopic', topic_new)],
        states = {
            TOPIC_TITLE: [MessageHandler(Filters.text, topic_title)],
            TOPIC_BODY: [MessageHandler(Filters.text, topic_body)],
            TOPIC_PARENTS: [RegexHandler('^(https://test.wfx.io/api/v1/topics/[0-9]+/)$', topic_parents)],
        },
        fallbacks = [CommandHandler('done', topic_done)],
    )
    dp.add_handler(topics_handler)

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
    dp.add_handler(CallbackQueryHandler(topic_callback))
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