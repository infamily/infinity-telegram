import requests 
import json
import urllib
import cStringIO
from constants import Constants


class Comment:
    url = 0
    topic = None
    text = ''
    claimed_hours = 0.0
    assumed_hours = 0.0

    def __init__(self, token = None, url= ''):
        self.url = url
        if url is '':
            return
        headers = {
            "Authorization": 'Token ' + token,
        }
        response = requests.get(url, headers = headers)
        self.set(json.loads(response.text))

    @staticmethod
    def comments(token):
        headers = {
            "Authorization": 'Token ' + token,
        }
        response = requests.get(Constants.COMMENT_API_PATH, headers = headers)
        _comments = json.loads(response.text)
        comments = []
        for _t in _comments:
            comment = Comment()
            comment.set(_t)
            comments.append(comment)
        return comments

    def update(self, token):
        headers = {
            "Authorization": 'Token ' + token,
        }
        response = requests.put(self.url,
                                data = self.getData(),
                                headers = headers)

    def create(self, token):
        if self.url is not '':
            return
        headers = {
            "Authorization": 'Token ' + token,
        }
        response = requests.post(Constants.COMMENT_API_PATH,
                                 data = self.getData(),
                                 headers = headers)
        self.set(json.loads(response.text))

    def set(self, _t):
        self.topic = _t['topic']
        self.text = _t['text']
        self.claimed_hours = _t['claimed_hours']
        self.assumed_hours = _t['assumed_hours']
        self.url = _t['url']

    def getData(self):
        return {
            'topic': self.topic,
            'text': self.text,
            'claimed_hours': self.claimed_hours,
            'assumed_hours': self.assumed_hours,
        }