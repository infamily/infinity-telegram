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
from telegram.ext import Updater, Filters, CommandHandler, MessageHandler, ConversationHandler, CallbackQueryHandler, InlineQueryHandler, RegexHandler, ChosenInlineResultHandler

from user import User
from topic import Topic
from comment import Comment
from constants import Constants

# Enable logging
logging.basicConfig(format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level = logging.INFO)

logger = logging.getLogger(__name__)

# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.

AUTH_EMAIL, AUTH_CAPTCHA, AUTH_PASSWORD = range(3)
TOPIC_TITLE, TOPIC_BODY, TOPIC_PARENTS, TOPIC_DELETE, TOPIC_UPDATE, TOPIC_CALLBACK = range(6)
COMMENT_TEXT, COMMENT_TOPIC, COMMENT_DELETE, COMMENT_UPDATE, COMMENT_CALLBACK = range(5)


# Test value
user = User('longx695@gmail.com')
user.token = token
data['user'] = user


# user authentication
def auth_register(bot, update, chat_data):
    update.message.reply_text('What\'s your e-mail?')
    return AUTH_EMAIL

def auth_email(bot, update, chat_data):
    user_email = update.message.text
    if not re.match(Constants.EMAIL_PATTERN, user_email):
        update.message.reply_text('Please enter valid email')
        return AUTH_EMAIL
    user = User(user_email)
    captcha = user.get_captcha()
    data['user'] = user
    data['captcha'] = captcha
    bot.sendPhoto(chat_id = update.message.chat_id,
                  photo = Constants.SERVER_PATH + captcha['image_url'])
    update.message.reply_text('Please, solve the captcha.')
    return AUTH_CAPTCHA

def auth_captcha(bot, update, chat_data):
    captcha_value = update.message.text
    if 'user' not in data or 'captcha' not in data:
        print ('captcha_error')
        return
    user = data['user']
    captcha = data['captcha']
    res = user.signup(captcha['key'], captcha_value)
    if res.status_code == 200:
        token = json.loads(res.text)['token']
        del data['captcha']
        data['token'] = token
        update.message.reply_text('Please input OTP password')
        return AUTH_PASSWORD
    else:
        captcha = json.loads(res.content)
        data['captcha'] = captcha
        bot.sendPhoto(chat_id = update.message.chat_id,
                      photo = Constants.SERVER_PATH + captcha['image_url'])
        update.message.reply_text('Please, solve the captcha.')
        return AUTH_CAPTCHA

def auth_password(bot, update, chat_data):
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

def user_logout(bot, update, chat_data):
    if 'user' not in data or 'token' not in data:
        update.message.reply_text('You need to login in order to logout')
        return
    del data['user']
    del data['token']
    update.message.reply_text('Logged out!')
def user_status(bot, update, chat_data):
    if 'user' not in data or 'token' not in data:
        update.message.reply_text('You are not logged in')
        return
    user = data['user']
    update.message.reply_text('(' + user.email + ') is logged in')

# topics
def topic_new(bot, update, chat_data):
    if ('user' not in data or token is ''):
        update.message.reply_text('You have to login to create a topic. Please use /register to login')
        return ConversationHandler.END
    _topic = Topic()
    data['_topic'] = _topic
    data['topic_command_type'] = "post"
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
    return TOPIC_CALLBACK

def topic_title(bot, update, chat_data):
    _topic = data['_topic']
    if _topic.type is -1:
        return
    title = update.message.text
    _topic.title = title
    if data['topic_command_type'] == 'update':
        update.message.reply_text('Title: %s' % title)
        return TOPIC_CALLBACK
    else:
        update.message.reply_text('Title: %s\nPlease input body.' % title)
        return TOPIC_BODY

def topic_body(bot, update, chat_data):
    print ('topic_body')
    body = update.message.text
    _topic = data['_topic']
    _topic.body = body
    data['topics'] = Topic.topics(token)
    if data['topic_command_type'] == 'update':
        update.message.reply_text('Body: %s' % body)
        return TOPIC_CALLBACK
    else:
        keyboard = [[InlineKeyboardButton("Select Parents", switch_inline_query_current_chat = "Topics:")]]
        update.message.reply_text('Body: %s\nSelect Parents' % body,
                                  reply_markup = InlineKeyboardMarkup(keyboard))
        return TOPIC_CALLBACK

def topic_parents(bot, update, chat_data):
    parent = update.message.text

    print ("topic_parents")
    # topics = Topic.topics(token)
    # _topic = data['_topic']
    # if parent in _topic.parents:
    #     return
    # if parent in topics:
    #     _topic.parents.append(parent)
    # if data['topic_command_type'] == 'update':
    #     return TOPIC_CALLBACK
    # else:
    #     return topic_finish(bot, update.message.chat_id)

def topic_delete(bot, update, chat_data):
    if ('user' not in data or token is ''):
        update.message.reply_text('You have to login to create a topic. Please use /register to login')
        return ConversationHandler.END
    keyboard = [
        [
            InlineKeyboardButton("Topics", switch_inline_query_current_chat = "Topics:"),
        ]
    ]
    data['topic_command_type'] = "delete"
    update.message.reply_text('Please choose:', reply_markup = InlineKeyboardMarkup(keyboard))
    return TOPIC_DELETE

def topic_delete_selected(bot, update, chat_data):
    url = update.message.text
    _topic = Topic(token, url)
    data['_topic'] = _topic
    bot.send_message(chat_id = update.message.chat_id,
                     text = "Please type /done to finish")

def topic_update(bot, update, chat_data):
    if ('user' not in data or token is ''):
        update.message.reply_text('You have to login to create a topic. Please use /register to login')
        return ConversationHandler.END
    keyboard = [
        [
            InlineKeyboardButton("Select Topics", switch_inline_query_current_chat = "Topics:"),
        ]
    ]
    update.message.reply_text('Please choose:', reply_markup = InlineKeyboardMarkup(keyboard))
    return TOPIC_UPDATE

def topic_update_properties(bot, update, chat_data):
    url = update.message.text
    _topic = Topic(token, url)
    keyboard = [
        [
            InlineKeyboardButton("Type", callback_data = '11'),
            InlineKeyboardButton("Title", callback_data = '12'),
        ],
        [
            InlineKeyboardButton("Body", callback_data = '13'),
            InlineKeyboardButton("Parents", callback_data = '14'),
        ],
        [
            InlineKeyboardButton("Update", callback_data = '7'),
        ]
    ]
    data['topic_command_type'] = "update"
    data['_topic'] = _topic
    update.message.reply_text('What would you like to update?:', reply_markup = InlineKeyboardMarkup(keyboard))
    return TOPIC_CALLBACK

def parents_callback(bot, update):
    print ("parents_callback")

def topic_callback(bot, update, chat_data):
    query = update.callback_query
    message = query.message
    chat_id = message.chat_id
    message_id = message.message_id
    print ("callback: %s" % query.data)
    type = int(query.data)
    if type < 5:
        _topic = data['_topic']
        _topic.type = type
        types = ['Need', 'Goal', 'Idea', 'Plan', 'Task']
        if data['topic_command_type'] == 'update':
            bot.edit_message_text(text = "Type: %s" % types[type],
                                chat_id = chat_id,
                                message_id = message_id)
            return TOPIC_CALLBACK
        else:
            bot.edit_message_text(text = "Type: %s\nPlease input Title." % types[type],
                                chat_id = chat_id,
                                message_id = message_id)
            return TOPIC_TITLE
    elif type is 6:
        bot.edit_message_text(text = "Please type /done to finish",
                              chat_id = chat_id,
                              message_id = message_id)
    elif type is 7:
        return topic_finish(bot, chat_id)
    elif type is 11:
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
        bot.send_message(text = "Please select type",
                         chat_id = chat_id,
                         reply_markup = InlineKeyboardMarkup(keyboard))
    elif type is 12:
        bot.send_message(text = "Please input Title:",
                         chat_id = chat_id)
        return TOPIC_TITLE
    elif type is 13:
        bot.send_message(text = "Please input Body:",
                         chat_id = chat_id)
        return TOPIC_BODY
    elif type is 14:
        keyboard = [[InlineKeyboardButton("Select Parents", switch_inline_query_current_chat = "Topics:")]]
        bot.send_message(text = "Please select parents:",
                         chat_id = chat_id,
                         reply_markup = InlineKeyboardMarkup(keyboard))
        # return PARENT_CALLBACK
    else:
        print ('parents')

def topic_done(bot, update, chat_data):
    return topic_finish(bot, update.message.chat_id)

def topic_finish(bot, chat_id):
    _topic = data['_topic']
    topic_command_type = data['topic_command_type']
    if topic_command_type is 'post':
        _topic.create(token)
        bot.send_message(chat_id = chat_id,
                         text = 'New topic has been created')
    elif topic_command_type is 'delete':
        bot.send_message(chat_id = chat_id,
                         text = 'A topic has been deleted')
        _topic.delete(token)
    else :
        bot.send_message(chat_id = chat_id,
                         text = 'A topic has been updated')
    return ConversationHandler.END

# comment
def comment_new(bot, update, chat_data):
    if ('user' not in data or token is ''):
        update.message.reply_text('You have to login to create a topic. Please use /register to login')
        return ConversationHandler.END
    _comment = Comment()
    data['_comment'] = _comment
    data['comment_command_type'] = "post"
    keyboard = [[InlineKeyboardButton("Select Topic", switch_inline_query_current_chat = 'Topics:')]]
    update.message.reply_text('Select Topic', reply_markup = InlineKeyboardMarkup(keyboard))
    return COMMENT_TOPIC

def comment_topic(bot, update, chat_data):
    topic = update.message.text
    topics = Topic.topics(token)
    if topic in topic:
        _comment = data['_comment']
        _comment.topic = topic
        if data['comment_command_type'] == 'update':
            return COMMENT_CALLBACK
        else:
            update.message.reply_text('Please input text.')
            return COMMENT_TEXT

def comment_text(bot, update, chat_data):
    _comment = data['_comment']
    text = update.message.text
    _comment.text = text
    if data['comment_command_type'] == 'update':
        update.message.reply_text('Text: %s' % text)
        return COMMENT_CALLBACK
    else:
        update.message.reply_text('Text: %s\n' % text)
        return comment_finish(bot, update.message.chat_id)

def comment_update(bot, update, chat_data):
    if ('user' not in data or token is ''):
        update.message.reply_text('You have to login to create a topic. Please use /register to login')
        return ConversationHandler.END
    keyboard = [
        [
            InlineKeyboardButton("Select Comments", switch_inline_query_current_chat = "Comment:"),
        ]
    ]
    update.message.reply_text('Please choose:', reply_markup = InlineKeyboardMarkup(keyboard))
    return COMMENT_UPDATE

def comment_delete_selected(bot, update, chat_data):
    url = update.message.text
    _comment = Comment(token, url)
    data['_comment'] = _comment
    bot.send_message(chat_id = update.message.chat_id,
                     text = "Please type /done to finish")

def comment_update_properties(bot, update, chat_data):
    url = update.message.text
    _comment = Comment(token, url)
    keyboard = [
        [
            InlineKeyboardButton("Topic", callback_data = '1'),
            InlineKeyboardButton("Text", callback_data = '2'),
        ],
        [
            InlineKeyboardButton("Update", callback_data = '3'),
        ]
    ]
    data['comment_command_type'] = "update"
    data['_comment'] = _comment
    update.message.reply_text('What would you like to update?:', reply_markup = InlineKeyboardMarkup(keyboard))
    return COMMENT_CALLBACK

def comment_callback(bot, update, chat_data):
    query = update.callback_query
    message = query.message
    chat_id = message.chat_id
    message_id = message.message_id
    type = int(query.data)
    if type is 1:
        keyboard = [[InlineKeyboardButton("Select Topic", switch_inline_query_current_chat = "Topics:")]]
        bot.send_message(text = "Please select topic:",
                         chat_id = chat_id,
                         reply_markup = InlineKeyboardMarkup(keyboard))
        return COMMENT_TOPIC
    elif type is 2:
        bot.send_message(text = "Please input Text:",
                         chat_id = chat_id)
        return COMMENT_TEXT
    elif type is 3:
        return comment_finish(bot, chat_id)
    else:
        print ('parents')

def comment_delete(bot, update,chat_data):
    if ('user' not in data or token is ''):
        update.message.reply_text('You have to login to create a topic. Please use /register to login')
        return ConversationHandler.END
    keyboard = [
        [
            InlineKeyboardButton("Comment:", switch_inline_query_current_chat = "Comment:"),
        ]
    ]
    data['comment_command_type'] = "delete"
    update.message.reply_text('Please choose:', reply_markup = InlineKeyboardMarkup(keyboard))
    return COMMENT_DELETE

def comment_done(bot, update, chat_data):
    return comment_finish(bot, update.message.chat_id)

def comment_finish(bot, chat_id):
    _comment = data['_comment']
    comment_command_type = data['comment_command_type']
    if comment_command_type is 'post':
        _comment.create(token)
        bot.send_message(chat_id = chat_id,
                         text = 'New comment has been created')
    elif comment_command_type is 'delete':
        bot.send_message(chat_id = chat_id,
                         text = 'A comment has been deleted')
        _comment.delete(token)
    else :
        bot.send_message(chat_id = chat_id,
                         text = 'A comment has been updated')
    return ConversationHandler.END

def inline_query(bot, update):
    query = update.inline_query.query
    query = query.decode('utf-8')
    results = list()
    if 'Topics:' in query:
        query = remove_prefix(query, 'Topics:')
        topics = Topic.topics(token, query)
        for topic in topics:
            keyboard = [[InlineKeyboardButton(topic.title, callback_data = topic.url)]]
            results.append(InlineQueryResultArticle(id = uuid4(),
                                                    title = topic.title,
                                                    input_message_content = InputTextMessageContent('Topic:'),
                                                    reply_markup = InlineKeyboardMarkup(keyboard)))
        # update.inline_query.answer(results, cache_time = 5)
    elif 'Comment:' in query:
        query = remove_prefix(query, 'Comment:')
        comments = Comment.comments(token, query)
        for comment in comments:
            results.append(InlineQueryResultArticle(id = uuid4(),
                                                    title = comment.url,
                                                    input_message_content = InputTextMessageContent(comment.url)))
        # update.inline_query.answer(results, cache_time = 5)
    else:
        print "error"
    bot.answerInlineQuery(update.inline_query.id, results, cache_time=0)

def remove_prefix(text, prefix):
    if text.startswith(prefix):
        return text[len(prefix):]
    return text

def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))

def main():
    # Create the EventHandler and pass it your bot's token.
    updater = Updater('421683175:AAErGVBS_Av0XD5dz-rWHBuZinPYDP0_wCg')
    # Get the dispatcher to register handlers
    dp = updater.dispatcher
    # on different commands - answer in Telegram
    auth_handler = ConversationHandler(
        entry_points = [CommandHandler('register', auth_register, pass_chat_data = True)],
        states = {
            AUTH_EMAIL: [MessageHandler(Filters.text, auth_email, pass_chat_data = True)],
            AUTH_CAPTCHA: [MessageHandler(Filters.text, auth_captcha, pass_chat_data = True)],
            AUTH_PASSWORD: [MessageHandler(Filters.text, auth_password, pass_chat_data = True)]
        },
        fallbacks = [CommandHandler('cancel', error)]
    )
    dp.add_handler(auth_handler)
    dp.add_handler(CommandHandler("logout", user_logout, pass_chat_data = True))
    dp.add_handler(CommandHandler("status", user_status, pass_chat_data = True))
    topics_handler = ConversationHandler(
        entry_points = [
            CommandHandler('newtopic', topic_new, pass_chat_data = True),
            CommandHandler('deletetopic', topic_delete, pass_chat_data = True),
            CommandHandler('updatetopic', topic_update, pass_chat_data = True)],
        states = {
            TOPIC_TITLE: [MessageHandler(Filters.text, topic_title, pass_chat_data = True)],
            TOPIC_BODY: [MessageHandler(Filters.text, topic_body, pass_chat_data = True)],
            TOPIC_PARENTS: [RegexHandler(Constants.TOPIC_URL_PATTERN, topic_parents, pass_chat_data = True)],
            TOPIC_DELETE: [RegexHandler(Constants.TOPIC_URL_PATTERN, topic_delete_selected, pass_chat_data = True)],
            TOPIC_UPDATE: [RegexHandler(Constants.TOPIC_URL_PATTERN, topic_update_properties, pass_chat_data = True)],
            TOPIC_CALLBACK: [CallbackQueryHandler(topic_callback, pass_chat_data = True)],
        },
        fallbacks = [CommandHandler('done', topic_done, pass_chat_data = True)],
    )
    dp.add_handler(topics_handler)

    comment_handler = ConversationHandler(
        entry_points = [
            CommandHandler('newcomment', comment_new, pass_chat_data = True),
            CommandHandler('deletecomment', comment_delete, pass_chat_data = True),
            CommandHandler('updatecomment', comment_update, pass_chat_data = True)],
        states = {
            COMMENT_TOPIC: [RegexHandler(Constants.TOPIC_URL_PATTERN, comment_topic, pass_chat_data = True)],
            COMMENT_TEXT: [MessageHandler(Filters.text, comment_text, pass_chat_data = True)],
            COMMENT_UPDATE: [RegexHandler(Constants.COMMENT_URL_PATTERN, comment_update_properties, pass_chat_data = True)],
            COMMENT_DELETE: [RegexHandler(Constants.COMMENT_URL_PATTERN, comment_delete_selected, pass_chat_data = True)],
            COMMENT_CALLBACK: [CallbackQueryHandler(comment_callback, pass_chat_data = True)]
        },
        fallbacks = [CommandHandler('done', comment_done, pass_chat_data = True)],
    )
    dp.add_handler(comment_handler)
    dp.add_handler(InlineQueryHandler(inline_query))
    dp.add_handler(ChosenInlineResultHandler(parents_callback))

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