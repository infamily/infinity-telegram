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

from telegram import ReplyKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Updater, Filters, CommandHandler, MessageHandler, ConversationHandler
import telegram

import logging
import re
import json

from user import User
from constants import SERVER_PATH

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger=logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.

AUTH_EMAIL, AUTH_CAPTCHA, AUTH_PASSWORD=range(3)

# user authentication
def auth_register(bot, update):
    update.message.reply_text('What\'s your e-mail?')
    return AUTH_EMAIL
def auth_email(bot, update, chat_data):
    user_email=update.message.text
    if not re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', user_email):
        update.message.reply_text('Please enter valid email')
        return AUTH_EMAIL
    bot.send_chat_action(chat_id=update.message.chat_id, action=telegram.ChatAction.TYPING)
    user=User(user_email)
    captcha=user.get_captcha()
    chat_data['user']=user
    chat_data['captcha']=captcha
    bot.sendPhoto(chat_id=update.message.chat_id, photo=SERVER_PATH + captcha['image_url'])
    update.message.reply_text('Please, solve the captcha.')
    return AUTH_CAPTCHA
def auth_captcha(bot, update, chat_data):
    captcha_value=update.message.text
    if 'user' not in chat_data or 'captcha' not in chat_data :
        print ('captcha_error')
        return
    user=chat_data['user']
    captcha=chat_data['captcha']
    res=user.signup(captcha['key'], captcha_value)
    if res.status_code == 200 :
        print res.text
        token=json.loads(res.text)['token']
        del chat_data['captcha']
        chat_data['token']=token
        update.message.reply_text('Please input OTP password')
        return AUTH_PASSWORD
    else:
        captcha=json.loads(res.content)
        chat_data['captcha']=captcha
        bot.sendPhoto(chat_id=update.message.chat_id, photo=SERVER_PATH + captcha['image_url'])
        update.message.reply_text('Please, solve the captcha.')
        return AUTH_CAPTCHA
def auth_password(bot, update, chat_data):
    password=update.message.text
    if 'user' not in chat_data or 'token' not in chat_data :
        print ('password_error')
        return
    user=chat_data['user']
    token=chat_data['token']
    if user.login(token, password):
        update.message.reply_text('Login Successed')
        return ConversationHandler.END
    else :
        update.message.reply_text('Login Failed')
# 
def user_logout(bot, update, chat_data):
    if 'user' not in chat_data or 'token' not in chat_data :
        update.message.reply_text('You need to login in order to logout')
        return
    del chat_data['user']
    del chat_data['token']
    update.message.reply_text('Logged out!')
def user_status(bot, update, chat_data):
    if 'user' not in chat_data or 'token' not in chat_data :
        update.message.reply_text('You are not logged in')
        return
    user=chat_data['user']
    update.message.reply_text('(' + user.email + ') is logged in')

def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))

def main():
    # Create the EventHandler and pass it your bot's token.
    updater=Updater('421683175:AAErGVBS_Av0XD5dz-rWHBuZinPYDP0_wCg')

    # Get the dispatcher to register handlers
    dp=updater.dispatcher

    # on different commands - answer in Telegram

    auth_handler=ConversationHandler(
        entry_points=[CommandHandler('register', auth_register)],
        states={
            AUTH_EMAIL: [MessageHandler(Filters.text, auth_email, pass_chat_data=True)],
            AUTH_CAPTCHA: [MessageHandler(Filters.text, auth_captcha, pass_chat_data=True)],
            AUTH_PASSWORD: [MessageHandler(Filters.text, auth_password, pass_chat_data=True)]
        },
        fallbacks=[CommandHandler('cancel', error)]
    )
    dp.add_handler(auth_handler)
    dp.add_handler(CommandHandler("logout", user_logout, pass_chat_data=True))
    dp.add_handler(CommandHandler("status", user_status, pass_chat_data=True))

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