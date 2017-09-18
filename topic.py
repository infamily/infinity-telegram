import requests 
import json
import urllib
import cStringIO
from constants import Constants

class Topic:
    url = ''
    type = -1
    title = ''
    body = ''
    parents = []

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

    def __init__(self, token = None, url = ''):
        if url is '':
            return
        headers = {
            "Authorization": 'Token ' + token,
        }
        response = requests.get(url, headers = headers)
        self.set(json.loads(response.text))

    @staticmethod
    def topics(token, title=''):
        headers = {
            "Authorization": 'Token ' + token,
        }
        response = requests.get(Constants.TOPIC_API_PATH + "?search=%s" % title, headers = headers)
        _topics = json.loads(response.text)
        topics = []
        for _t in _topics:
            topic = Topic()
            topic.set(_t)
            topics.append(topic)
        return topics

    def update(self, token):
        headers = {
            "Authorization": 'Token ' + token,
        }
        response = requests.put(self.url,
                                data = self.getData(),
                                headers = headers)

    def create(self, token):
        if self.url is not '':
            print 'already created'
            return
        headers = {
            "Authorization": 'Token ' + token,
        }
        response = requests.post(Constants.TOPIC_API_PATH,
                                 data = self.getData(),
                                 headers = headers)
        self.set(json.loads(response.text))

    def delete(self, token):
        headers = {
            "Authorization": 'Token ' + token,
        }
        response = requests.delete(self.url,
                                   headers = headers)
    def set(self, _t):
        self.type = _t['type']
        self.title = _t['title']
        self.body = _t['body']
        self.parents = _t['parents']
        self.url = _t['url']

    def getData(self):
        return {
            'type': self.type,
            'title': self.title,
            'body': self.body,
            'parents': self.parents,
        }