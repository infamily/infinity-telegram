#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import uuid
import json
import logging
import requests
import urllib.parse

logging.basicConfig(
    format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level = logging.INFO
)
logger = logging.getLogger(__name__)

import telegram

from telegram import (
    ReplyKeyboardMarkup,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    InlineQueryResultArticle,
    InputTextMessageContent,
    ParseMode
)

from telegram.ext import (
    Updater,
    Filters,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    CallbackQueryHandler,
    InlineQueryHandler,
    RegexHandler,
    ChosenInlineResultHandler
)

class Config:
    SERVER_PATH = 'https://test.wfx.io'
    TELEGRAM_BOT_TOKEN = '422394624:AAEtMdP9ghRkcvOqKgX2YN5WjwmlUMylgsY'

config = Config()


class Constants:
    EMAIL_PATTERN = '^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    TOPIC_URL_PATTERN = '^({base}/api/v1/topics/[0-9]+/)$'.format(base=config.SERVER_PATH)
    COMMENT_URL_PATTERN = '^({base}/api/v1/comments/[0-9]+/)$'.format(base=config.SERVER_PATH)
    TOPIC_API_PATH = '{base}/api/v1/topics/'.format(base=config.SERVER_PATH)
    COMMENT_API_PATH = '{base}/api/v1/comments/'.format(base=config.SERVER_PATH)

constants = Constants()


class User:

    def __init__(self, email='long'):
        self.email = email
        self.token = str()

    def get_captcha(self):
        response = requests.get(urllib.parse.urljoin(config.SERVER_PATH, '/otp/singup'))
        if not response.ok:
            return
        captcha = json.loads(response.text)
        return captcha

    def get_captcha_image(self, url):
        logging.info('getCaptchaImage')

    def login(self, token, password):
        data = {'password': password }
        headers = {"Authorization": 'Token {}'.format(token)}

        response = requests.post(
            urllib.parse.urljoin(config.SERVER_PATH, '/otp/login/'),
            data=json.dumps(data),
            headers=headers
        )
        self.token = token
        return response.ok

    def signup(self, captcha, key):
        data = {
            'email': self.email,
            'captcha_0': captcha,
            'captcha_1': key
        }
        response = requests.post(
            urllib.parse.urljoin(config.SERVER_PATH, '/otp/singup/'),
            data=json.dumps(data)
        )
        # Sometimes returns 400
        # if not response.ok:
        #     import ipdb; ipdb.set_trace()

        return response

user = User()

class Topic:

    NEED = 0
    GOAL = 1
    IDEA = 2
    PLAN = 3
    TASK = 4

    TOPIC_TYPES = [
        (NEED, 'Need'),
        (GOAL, 'Goal'),
        (IDEA, 'Idea'),
        (PLAN, 'Plan'),
        (TASK, 'Task'),
    ]

    def __init__(self, token=None, url=''):

        self.url = url
        self.type = -1
        self.title = str()
        self.body = str()
        self.parents = []

        if url is '':
            return

        headers = {"Authorization": 'Token {}'.format(token)}
        response = requests.get(url, headers=headers)
        self.set(json.loads(response.text))

    @staticmethod
    def topics(self, token, title=''):
        headers = {"Authorization": 'Token {}'.format(token)}

        response = requests.get(
            '{}?search={}'.format(constants.TOPIC_API_PATH, title),
            headers=headers,
        )

        if response.ok:

            _topics = json.loads(response.text)
            topics = []
            for _t in _topics:
                try:
                    topic = Topic()
                    topic.set(_t)
                    topics.append(topic)
                except:
                    import ipdb; ipdb.set_trace()
            return topics

        else:
            logging.error(response.content)

    def update(self, token):
        headers = {"Authorization": 'Token {}'.format(token)}

        response = requests.put(
            self.url,
            data = self.get_data(),
            headers = headers
        )

    def create(self, token):
        if self.url is not '':
            logging.info('already created')
            return
        headers = {"Authorization": 'Token {}'.format(token)}
        response = requests.post(
            constants.TOPIC_API_PATH,
            data = self.get_data(),
            headers = headers
        )
        self.set(json.loads(response.text))

    def delete(self, token):
        headers = {"Authorization": 'Token {}'.format(token)}
        response = requests.delete(
            self.url,
            headers=headers
        )

    def set(self, _t):
        self.type = _t['type']
        self.title = _t['title']
        self.body = _t['body']
        self.parents = _t['parents']
        self.url = _t['url']

    def get_data(self):
        return {
            'type': self.type,
            'title': self.title,
            'body': self.body,
            'parents': self.parents,
        }


class Comment:

    def __init__(self, token=None, url=''):

        self.url = 0
        self.topic = None
        self.text = ''
        self.claimed_hours = 0.0
        self.assumed_hours = 0.0
        self.url = url

        if url is '':
            return

        headers = {"Authorization": 'Token {}'.format(token)}
        response = requests.get(url, headers=headers)
        self.set(json.loads(response.text))

    @staticmethod
    def comments(self, token, text=''):
        headers = {"Authorization": 'Token {}'.format(token)}
        response = requests.get(
            "{}?search=%s".format(constants.COMMENT_API_PATH, text),
             headers = headers
        )
        _comments = json.loads(response.text)
        comments = []
        for _t in _comments:
            comment = Comment()
            comment.set(_t)
            comments.append(comment)
        return comments

    def update(self, token):
        headers = {"Authorization": 'Token {}'.format(token)}
        response = requests.put(
            self.url,
            data = self.get_data(),
            headers = headers
        )

    def create(self, token):
        if not self.url:
            return
        headers = {"Authorization": 'Token {}'.format(token)}
        response = requests.post(
            constants.COMMENT_API_PATH,
            data=self.get_data(),
            headers=headers
        )
        self.set(json.loads(response.text))

    def set(self, _t):
        self.topic = _t['topic']
        self.text = _t['text']
        self.claimed_hours = _t['claimed_hours']
        self.assumed_hours = _t['assumed_hours']
        self.url = _t['url']

    def get_data(self):
        return {
            'topic': self.topic,
            'text': self.text,
            'claimed_hours': self.claimed_hours,
            'assumed_hours': self.assumed_hours,
        }
    def delete(self, token):
        headers = {"Authorization": 'Token {}'.format(token)}

        response = requests.delete(
            self.url,
            headers = headers
        )


class Agent:

    def __init__(self):
        self.data = {}

    #################  AUTHENTICATION  ################# 

    def auth_register(self, bot, update, chat_data):
        update.message.reply_text("What's your e-mail?")
        return AUTH_EMAIL

    def auth_email(self, bot, update, chat_data):

        user_email = update.message.text

        if not re.match(constants.EMAIL_PATTERN, user_email):
            update.message.reply_text('Please enter valid email')
            return AUTH_EMAIL

        user = User(user_email)
        captcha = user.get_captcha()
        self.data['user'] = user
        self.data['captcha'] = captcha

        logger.info('CAPTCHA: {}'.format(captcha))

        bot.sendPhoto(
            chat_id = update.message.chat_id,
            photo = urllib.parse.urljoin(config.SERVER_PATH, captcha['image_url'])
        )

        update.message.reply_text('Please, solve the captcha.')
        return AUTH_CAPTCHA

    def auth_captcha(self, bot, update, chat_data):
        captcha_value = update.message.text

        if 'user' not in self.data or 'captcha' not in self.data:
            logger.error('captcha_error')
            return

        user = self.data.get('user')
        captcha = self.data.get('captcha')
        response = user.signup(captcha.get('key'), captcha_value)

        if response.ok:
            token = json.loads(response.text).get('token')
            del self.data['captcha']
            self.data['token'] = token
            update.message.reply_text('Please input OTP password')
            return AUTH_PASSWORD

        else:
            captcha = json.loads(response.content)
            self.data['captcha'] = captcha
            bot.sendPhoto(
                chat_id=update.message.chat_id,
                photo=urllib.parse.urljoin(config.SERVER_PATH, captcha['image_url'])
            )
            update.message.reply_text('Please, solve the captcha.')
            return AUTH_CAPTCHA

    def auth_password(self, bot, update, chat_data):
        password = update.message.text

        if 'user' not in self.data or 'token' not in self.data:
            logger.error('password_error')
            return

        user = self.data.get('user')
        token = self.data.get('token')

        if user.login(token, password):
            update.message.reply_text('Login Successed')
            return ConversationHandler.END

        else:
            update.message.reply_text('Login Failed')

    def user_logout(bot, update, chat_data):

        if 'user' not in self.data or 'token' not in self.data:
            update.message.reply_text('You need to login in order to logout')
            return

        del data['user']
        del data['token']
        update.message.reply_text('Logged out!')

    def user_status(bot, update, chat_data):

        if 'user' not in self.data or 'token' not in self.data:
            update.message.reply_text('You are not logged in')
            return

        user = data.get('user')
        update.message.reply_text('({}) is logged in'.format(user.email))

    #################  TOPIC  ################# 

    def topic_new(self, bot, update, chat_data):
        if ('user' not in self.data or not self.data.get('token')):
            update.message.reply_text('You have to login to create a topic. Please use /register to login')
            return ConversationHandler.END
        _topic = Topic()
        data['_topic'] = _topic
        data['topic_command_type'] = "post"
        keyboard = [
            [
                InlineKeyboardButton("Need", callback_data='0'),
                InlineKeyboardButton("Goal", callback_data='1'),
                InlineKeyboardButton("Idea", callback_data='2')
            ],
            [
                InlineKeyboardButton("Plan", callback_data='3'),
                InlineKeyboardButton("Task", callback_data='4')
            ]
        ]
        update.message.reply_text('Please choose:', reply_markup=InlineKeyboardMarkup(keyboard))
        return TOPIC_CALLBACK

    def topic_title(self, bot, update, chat_data):
        _topic = data['_topic']
        if _topic.type is -1:
            return
        title = update.message.text
        _topic.title = title
        if data['topic_command_type'] == 'update':
            update.message.reply_text('Title: {}'.format(title))
            return TOPIC_CALLBACK
        else:
            update.message.reply_text('Title: {}\nPlease input body.'.format(title))
            return TOPIC_BODY

    def topic_body(self, bot, update, chat_data):
        logger.info('topic_body')
        body = update.message.text
        _topic = data['_topic']
        _topic.body = body
        data['topics'] = Topic.topics(token)
        if data['topic_command_type'] == 'update':
            update.message.reply_text('Body: {}'.format(body))
            return TOPIC_CALLBACK
        else:
            keyboard = [[InlineKeyboardButton("Select Parents", switch_inline_query_current_chat="Topics:")]]
            update.message.reply_text(
                'Body: {}\nSelect Parents'.format(body),
                 reply_markup = InlineKeyboardMarkup(keyboard)
            )
            return TOPIC_CALLBACK

    def topic_parents(self, bot, update, chat_data):
        parent = update.message.text

        logging.info("topic_parents")
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

    def topic_delete(self, bot, update, chat_data):
        if ('user' not in self.data or not self.data.get('token')):
            update.message.reply_text('You have to login to create a topic. Please use /register to login')
            return ConversationHandler.END
        keyboard = [
            [
                InlineKeyboardButton("Topics", switch_inline_query_current_chat="Topics:"),
            ]
        ]
        data['topic_command_type'] = "delete"
        update.message.reply_text('Please choose:', reply_markup=InlineKeyboardMarkup(keyboard))
        return TOPIC_DELETE

    def topic_delete_selected(self, bot, update, chat_data):
        url = update.message.text
        _topic = Topic(token, url)
        data['_topic'] = _topic

        bot.send_message(
            chat_id = update.message.chat_id,
            text="Please type /done to finish"
        )

    def topic_update(self, bot, update, chat_data):
        if ('user' not in self.data or not self.data.get('token')):
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

    def parents_callback(self, bot, update):
        logging.info("parents_callback")

    def topic_callback(self, bot, update, chat_data):
        query = update.callback_query
        message = query.message
        chat_id = message.chat_id
        message_id = message.message_id
        logging.info("callback: {}".format(query.data))
        topic_type = int(query.data)

        if topic_type < 5:
            _topic = data['_topic']
            _topic.type = topic_type
            topic_types = ['Need', 'Goal', 'Idea', 'Plan', 'Task']
            if data['topic_command_type'] == 'update':
                bot.edit_message_text(
                    text="Type: {}".format(topic_types[type]),
                    chat_id=chat_id,
                    message_id=message_id
                )
                return TOPIC_CALLBACK
            else:
                bot.edit_message_text(text = "Type: %s\nPlease input Title." % topic_types[topic_type],
                                    chat_id = chat_id,
                                    message_id = message_id)
                return TOPIC_TITLE
        elif topic_type is 6:
            bot.edit_message_text(text = "Please type /done to finish",
                                  chat_id = chat_id,
                                  message_id = message_id)
        elif topic_type is 7:
            return topic_finish(bot, chat_id)
        elif topic_type is 11:
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
            bot.send_message(
                text="Please select type",
                chat_id=chat_id,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        elif topic_type is 12:
            bot.send_message(
                text="Please input Title:",
                chat_id=chat_id
            )
            return TOPIC_TITLE
        elif topic_type is 13:
            bot.send_message(
                text="Please input Body:",
                chat_id=chat_id
            )
            return TOPIC_BODY
        elif topic_type is 14:
            keyboard = [[InlineKeyboardButton("Select Parents", switch_inline_query_current_chat = "Topics:")]]
            bot.send_message(
                text="Please select parents:",
                chat_id=chat_id,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            # return PARENT_CALLBACK
        else:
            logging.info('parents')

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


    #################  COMMENT  ################# 


    def comment_new(self, bot, update, chat_data):
        if ('user' not in self.data or not self.data.get('token')):
            update.message.reply_text('You have to login to create a topic. Please use /register to login')
            return ConversationHandler.END
        _comment = Comment()
        data['_comment'] = _comment
        data['comment_command_type'] = "post"
        keyboard = [[InlineKeyboardButton("Select Topic", switch_inline_query_current_chat='Topics:')]]
        update.message.reply_text('Select Topic', reply_markup = InlineKeyboardMarkup(keyboard))
        return COMMENT_TOPIC

    def comment_topic(self, bot, update, chat_data):
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

    def comment_text(self, bot, update, chat_data):
        _comment = data['_comment']
        text = update.message.text
        _comment.text = text
        if data['comment_command_type'] == 'update':
            update.message.reply_text('Text: {}'.format(text))
            return COMMENT_CALLBACK
        else:
            update.message.reply_text('Text: {}\n'.format(text))
            return comment_finish(bot, update.message.chat_id)

    def comment_update(self, bot, update, chat_data):
        if ('user' not in self.data or not self.data.get('token')):
            update.message.reply_text('You have to login to create a topic. Please use /register to login')
            return ConversationHandler.END
        keyboard = [
            [
                InlineKeyboardButton("Select Comments", switch_inline_query_current_chat="Comment:"),
            ]
        ]
        update.message.reply_text('Please choose:', reply_markup=InlineKeyboardMarkup(keyboard))
        return COMMENT_UPDATE

    def comment_delete_selected(self, bot, update, chat_data):
        url = update.message.text
        _comment = Comment(token, url)
        data['_comment'] = _comment
        bot.send_message(
            chat_id=update.message.chat_id,
            text="Please type /done to finish"
        )

    def comment_update_properties(self, bot, update, chat_data):
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
        update.message.reply_text('What would you like to update?:', reply_markup=InlineKeyboardMarkup(keyboard))
        return COMMENT_CALLBACK

    def comment_callback(self, bot, update, chat_data):
        query = update.callback_query
        message = query.message
        chat_id = message.chat_id
        message_id = message.message_id
        topic_type = int(query.data)
        if topic_type is 1:
            keyboard = [[InlineKeyboardButton("Select Topic", switch_inline_query_current_chat="Topics:")]]
            bot.send_message(
                text = "Please select topic:",
                chat_id = chat_id,
                reply_markup = InlineKeyboardMarkup(keyboard)
            )
            return COMMENT_TOPIC
        elif topic_type is 2:
            bot.send_message(
                text = "Please input Text:",
                chat_id = chat_id
            )
            return COMMENT_TEXT
        elif topic_type is 3:
            return comment_finish(bot, chat_id)
        else:
            logging.info('parents')

    def comment_delete(self, bot, update, chat_data):
        if ('user' not in self.data or not self.data.get('token')):
            update.message.reply_text('You have to login to create a topic. Please use /register to login')
            return ConversationHandler.END
        keyboard = [
            [
                InlineKeyboardButton("Comment:", switch_inline_query_current_chat="Comment:"),
            ]
        ]
        data['comment_command_type'] = "delete"
        update.message.reply_text('Please choose:', reply_markup=InlineKeyboardMarkup(keyboard))
        return COMMENT_DELETE

    def comment_done(self, bot, update, chat_data):
        return comment_finish(bot, update.message.chat_id)

    def comment_finish(self, bot, chat_id):
        _comment = data['_comment']
        comment_command_type = data['comment_command_type']

        if comment_command_type is 'post':
            _comment.create(token)
            bot.send_message(
                chat_id=chat_id,
                text='New comment has been created'
            )
        elif comment_command_type is 'delete':
            bot.send_message(
                chat_id=chat_id,
                text='A comment has been deleted'
            )
            _comment.delete(token)
        else :
            bot.send_message(
                chat_id=chat_id,
                text='A comment has been updated'
            )
        return ConversationHandler.END


    #################  GENERAL  ################# 

    def inline_query(self, bot, update):
        query = update.inline_query.query
        query = query.decode('utf-8')
        results = list()
        if 'Topics:' in query:
            query = remove_prefix(query, 'Topics:')
            topics = Topic.topics(token, query)
            for topic in topics:
                keyboard = [[InlineKeyboardButton(topic.title, callback_data = topic.url)]]
                results.append(
                    InlineQueryResultArticle(
                        id = uuid4(),
                        title = topic.title,
                        input_message_content = InputTextMessageContent('Topic:'),
                        reply_markup = InlineKeyboardMarkup(keyboard)
                    )
                )
            # update.inline_query.answer(results, cache_time = 5)
        elif 'Comment:' in query:
            query = remove_prefix(query, 'Comment:')
            comments = Comment.comments(token, query)
            for comment in comments:
                results.append(
                    InlineQueryResultArticle(
                        id = uuid4(),
                        title = comment.url,
                        input_message_content = InputTextMessageContent(comment.url)
                    )
                )
            # update.inline_query.answer(results, cache_time = 5)
        else:
            logging.error("error")
        bot.answerInlineQuery(update.inline_query.id, results, cache_time=0)

    def remove_prefix(self, text, prefix):
        if text.startswith(prefix):
            return text[len(prefix):]
        return text

    def error(self, bot, update, error):
        logger.warn('Update "{}" caused error "{}"'.format(update, error))


# Dummy Constants
AUTH_EMAIL, AUTH_CAPTCHA, AUTH_PASSWORD = range(3)
TOPIC_TITLE, TOPIC_BODY, TOPIC_PARENTS, TOPIC_DELETE, TOPIC_UPDATE, TOPIC_CALLBACK = range(6)
COMMENT_TEXT, COMMENT_TOPIC, COMMENT_DELETE, COMMENT_UPDATE, COMMENT_CALLBACK = range(5)

def main():

    # Initialization
    agent = Agent()
    updater = Updater(config.TELEGRAM_BOT_TOKEN)
    dispatcher = updater.dispatcher

    # Handlers

    # AUTH
    auth_handler = ConversationHandler(
        entry_points = [CommandHandler('register', agent.auth_register, pass_chat_data=True)],
        states = {
            AUTH_EMAIL: [MessageHandler(Filters.text, agent.auth_email, pass_chat_data=True)],
            AUTH_CAPTCHA: [MessageHandler(Filters.text, agent.auth_captcha, pass_chat_data=True)],
            AUTH_PASSWORD: [MessageHandler(Filters.text, agent.auth_password, pass_chat_data=True)]
        },
        fallbacks = [CommandHandler('cancel', agent.error)]
    )
    dispatcher.add_handler(auth_handler)
    dispatcher.add_handler(CommandHandler("logout", agent.user_logout, pass_chat_data=True))
    dispatcher.add_handler(CommandHandler("status", agent.user_status, pass_chat_data=True))


    # TOPIC

    topics_handler = ConversationHandler(
        entry_points = [
            CommandHandler('newtopic', agent.topic_new, pass_chat_data=True),
            CommandHandler('deletetopic', agent.topic_delete, pass_chat_data=True),
            CommandHandler('updatetopic', agent.topic_update, pass_chat_data=True)],
        states = {
            TOPIC_TITLE: [MessageHandler(Filters.text, agent.topic_title, pass_chat_data=True)],
            TOPIC_BODY: [MessageHandler(Filters.text, agent.topic_body, pass_chat_data=True)],
            TOPIC_PARENTS: [RegexHandler(constants.TOPIC_URL_PATTERN, agent.topic_parents, pass_chat_data=True)],
            TOPIC_DELETE: [RegexHandler(constants.TOPIC_URL_PATTERN, agent.topic_delete_selected, pass_chat_data=True)],
            TOPIC_UPDATE: [RegexHandler(constants.TOPIC_URL_PATTERN, agent.topic_update_properties, pass_chat_data=True)],
            TOPIC_CALLBACK: [CallbackQueryHandler(agent.topic_callback, pass_chat_data=True)],
        },
        fallbacks = [CommandHandler('done', agent.topic_done, pass_chat_data = True)],
    )
    dispatcher.add_handler(topics_handler)


    # COMMENT

    comment_handler = ConversationHandler(
        entry_points = [
            CommandHandler('newcomment', agent.comment_new, pass_chat_data=True),
            CommandHandler('deletecomment', agent.comment_delete, pass_chat_data=True),
            CommandHandler('updatecomment', agent.comment_update, pass_chat_data=True)],
        states = {
            COMMENT_TOPIC: [RegexHandler(constants.TOPIC_URL_PATTERN, agent.comment_topic, pass_chat_data=True)],
            COMMENT_TEXT: [MessageHandler(Filters.text, agent.comment_text, pass_chat_data = True)],
            COMMENT_UPDATE: [RegexHandler(constants.COMMENT_URL_PATTERN, agent.comment_update_properties, pass_chat_data = True)],
            COMMENT_DELETE: [RegexHandler(constants.COMMENT_URL_PATTERN, agent.comment_delete_selected, pass_chat_data = True)],
            COMMENT_CALLBACK: [CallbackQueryHandler(agent.comment_callback, pass_chat_data = True)]
        },
        fallbacks = [CommandHandler('done', agent.comment_done, pass_chat_data=True)],
    )
    dispatcher.add_handler(comment_handler)
    dispatcher.add_handler(InlineQueryHandler(agent.inline_query))
    dispatcher.add_handler(ChosenInlineResultHandler(agent.parents_callback))


    # Polling
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
