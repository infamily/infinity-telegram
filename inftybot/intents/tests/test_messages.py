# coding: utf-8
from unittest import TestCase

from inftybot.intents import messages, states
from inftybot.intents.exceptions import ValidationError, CaptchaValidationError
from inftybot.models import User
from inftybot.tests.base import load_tg_updates, BotMixin, load_api_responses, mock_update
from inftybot.api.tests.base import APIMixin, patch_api_request
from inftybot.utils import update_from_dict

updates = load_tg_updates()
api_responses = load_api_responses()


class BaseIntentTestCase(BotMixin, APIMixin, TestCase):
    intent_cls = None

    def setUp(self):
        super(BaseIntentTestCase, self).setUp()
        self.bot = self.create_bot()
        self.api = self.create_api_client()

    def create_intent(self, update, **kwargs):
        update = update_from_dict(self.bot, update)
        mock_update(update)
        intent = self.intent_cls(
            bot=self.bot, update=update,
            api=self.api, **kwargs
        )
        return intent


class TestAuthIntent(messages.BaseAuthenticatedIntent):
    """Dummy"""
    def handle(self, *args, **kwargs):
        pass


class AuthenticatedIntentSetAuthenticationTestCase(BaseIntentTestCase):
    intent_cls = TestAuthIntent

    def test_call_intent_with_user_ensure_api_request_contains_token(self):
        update = updates['OTP_MESSAGE']

        user = User()
        user.token = 'token'
        user.email = 'example@email.com'

        intent = self.create_intent(update)

        try:
            intent(chat_data={
                'user': user,
            })
        except ValidationError:
            pass

        self.assertEqual(intent.api.session.headers['authorization'], 'Token token')

    def test_set_authentication_ensure_api_user_token_provided(self):
        intent = TestAuthIntent(api=self.api)
        user = User()
        user.email = 'example@email.com'
        intent.user = user
        intent.set_api_authentication('auth_token')
        self.assertEqual(
            intent.api.user.token, 'auth_token'
        )


class TestAuthEMailIntent(BaseIntentTestCase):
    intent_cls = messages.AuthEmailIntent

    def test_validate_email_valid_passes(self):
        update = updates['EMAIL_MESSAGE']
        intent = self.create_intent(update)
        intent.validate()

    def test_validate_email_invalid_raises(self):
        update = updates['EMAIL_MESSAGE']
        intent = self.create_intent(update)
        intent.update.message.text = ''
        with self.assertRaises(ValidationError):
            intent.validate()

    @patch_api_request(200, api_responses['SIGNUP'])
    def test_valid_email_returns_auth_state_captcha(self, api_response):
        update = updates['EMAIL_MESSAGE']
        intent = self.create_intent(update)
        rv = intent()
        self.assertEquals(rv, states.AUTH_STATE_CAPTCHA)

    def test_invalid_email_returns_no_state(self):
        update = updates['EMAIL_MESSAGE']
        intent = self.create_intent(update)
        intent.update.message.text = ''
        rv = intent()
        self.assertEquals(rv, None)


class TestAuthCaptchaIntent(BaseIntentTestCase):
    intent_cls = messages.AuthCaptchaIntent

    @patch_api_request(200, api_responses['SIGNUP_SUCCESS'])
    def test_valid_captcha_returns_auth_state_password(self, api_response):
        update = updates['CAPTCHA_MESSAGE']
        user = User()
        user.email = 'example@email.com'
        intent = self.create_intent(update, )
        rv = intent(chat_data={
            'user': user,
            'captcha': {'key': ''},
        })
        self.assertEquals(rv, states.AUTH_STATE_PASSWORD)

    @patch_api_request(400, api_responses['SIGNUP'])
    def test_invalid_captcha_returns_no_state(self, api_response):
        update = updates['CAPTCHA_MESSAGE']
        user = User()
        user.email = 'example@email.com'
        intent = self.create_intent(update)
        rv = intent(chat_data={
            'user': user,
            'captcha': {'key': 'key'}
        })
        self.assertEquals(rv, None)

    @patch_api_request(400, api_responses['SIGNUP'])
    def test_invalid_captcha_validation_error_raises(self, api_response):
        update = updates['CAPTCHA_MESSAGE']
        user = User()
        user.email = 'example@email.com'
        intent = self.create_intent(update, chat_data={
            'user': user,
            'captcha': {'key': 'key'}
        })
        with self.assertRaises(CaptchaValidationError):
            intent.validate()


class AuthOTPIntent(BaseIntentTestCase):
    intent_cls = messages.AuthOTPIntent

    @patch_api_request(403, api_responses['OTP_403'])
    def test_api_403_error_raises(self, api_response):
        update = updates['OTP_MESSAGE']

        user = User()
        user.token = 'token'
        user.email = 'example@email.com'

        intent = self.create_intent(update, chat_data={
            'user': user,
        })
        with self.assertRaises(ValidationError):
            intent.validate()

    @patch_api_request(403, api_responses['OTP_403'])
    def test_api_403_returns_no_state(self, api_response):
        update = updates['OTP_MESSAGE']

        user = User()
        user.token = 'token'
        user.email = 'example@email.com'

        intent = self.create_intent(update)
        rv = intent(chat_data={
            'user': user,
        })
        self.assertEqual(rv, None)

    @patch_api_request(200, '')
    def test_api_login_ok_return_state_end(self, api_response):
        update = updates['OTP_MESSAGE']

        user = User()
        user.token = 'token'
        user.email = 'example@email.com'

        intent = self.create_intent(update)
        rv = intent(chat_data={
            'user': user,
        })
        self.assertEquals(rv, states.STATE_END)
