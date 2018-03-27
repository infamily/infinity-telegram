# coding: utf-8
# flake8: noqa
from unittest import skip

from inftybot.core.intents.base import BaseIntent
from inftybot.core.tests.base import create_user_from_update, create_chat_from_update, load_tg_updates, \
    load_api_responses, BaseIntentTestCase

updates = load_tg_updates()
api_responses = load_api_responses()


class TestIntent(BaseIntent):
    def handle(self, *args, **kwargs):
        pass


class UpdateChatDataTestCase(BaseIntentTestCase):
    intent_cls = TestIntent

    # SKIP THIS TEST BECAUSE:
    # there is no working coneption how to merge stored chat data
    # and chat_data passed from TG (especially, how to determine outdated
    # keys and remove it)
    @skip
    def test_intent_call_passed_chat_data_stored_in_db(self):
        update = updates['OTP_MESSAGE']

        create_user_from_update(self.bot, update)
        chat = create_chat_from_update(self.bot, update)

        intent = self.create_intent(update)
        intent(chat_data={'test': 'complete'})

        chat_data = chat.ensure_chat_data()
        chat_data.refresh_from_db()
        self.assertEqual(chat_data.data['test'], 'complete')
