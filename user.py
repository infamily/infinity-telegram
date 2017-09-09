import requests 
 
import json
import urllib, cStringIO
from constants import SERVER_PATH

class User:
    email = ''
    token = ''
    def __init__(self, email):
        self.email = email

    def get_captcha(self):
        response = requests.get(SERVER_PATH + '/otp/singup')
        if response.status_code != 200 :
            return
        captcha = json.loads(response.text)
        return captcha

    def get_captcha_image(self, url):
        print ('getCaptchaImage')
        # file = cStringIO.StringIO(urllib.urlopen(url).read())
        # img = Image.open(file)

    def login(self, token, password):
        data = {
            'password': password,
        }
        headers = {
            "Authorization": 'Token ' + token,
        }
        response = requests.post(SERVER_PATH + '/otp/login/',
                                 data = json.dumps(data),
                                 headers = headers)
        print response.status_code
        self.token = token
        return response.status_code == 200

    def signup(self, captcha, key):
        data = {
            'email': self.email,
            'captcha_0': captcha,
            'captcha_1': key
        }
        response = requests.post(SERVER_PATH + '/otp/singup/',
                                 data = json.dumps(data))
        return response