# coding: utf-8
# flake8: noqa
import logging
import time
from random import randint
from unittest import TestCase

from botocore.exceptions import ClientError

from inftybot import storage

logger = logging.getLogger(__name__)


class DynamoStorageTestCase(TestCase):
    storage_cls = None

    def create_storage(self):
        cls = self.storage_cls
        if not cls.table_name.startswith('test_'):
            cls.table_name = 'test_{}'.format(cls.table_name)
        return self.storage_cls()

    def create_table(self):
        try:
            self.storage.create_table()

            while True:
                table = self.storage.describe_table()
                if table['TableStatus'] == 'ACTIVE':
                    break
                time.sleep(0.25)

        except ClientError as e:
            logger.error(e)

    def delete_table(self):
        try:
            self.storage.delete_table()
        except ClientError as e:
            logger.error(e)

    def setUp(self):
        self.storage = self.create_storage()
        self.create_table()

    def tearDown(self):
        pass
        # self.delete_table()


class UserDataStorageTestCase(DynamoStorageTestCase):
    storage_cls = storage.UserDataStorage

    def test_set_data_with_setitem_success(self):
        user_id = '1234567890'
        testvalue = randint(0, 99999)
        self.storage[user_id] = {'test': testvalue}

        rv = self.storage[user_id]
        self.assertEqual(rv['test'], testvalue)

    def test_get_from_storage_with_int_key(self):
        self.storage[123] = {'test': 1}
        value = self.storage[123]['test']
        self.assertEqual(value, 1)

    def test_update_storage_with_storage_data_as_data(self):
        self.storage[123] = {'test': 1}
        data = self.storage[123]
        data['test'] = 'complete'
        self.storage[123] = data
        self.assertEqual(self.storage[123]['test'], 'complete')

    def test_delete_storage_data_deleted(self):
        self.storage[123] = {'test': 1}
        del self.storage[123]
        self.assertFalse(self.storage[123])

    def test_delete_storage_unexisted_data_ok(self):
        self.storage[123] = {'test': 1}
        del self.storage[1234]


class StorageDataTestCase(DynamoStorageTestCase):
    storage_cls = storage.UserDataStorage

    def test_storage_data__setitem__changed_is_True(self):
        data = self.storage['test']
        data['key'] = 'value'
        self.assertTrue(data.is_changed)

    def test_storage_data__full_replace__changed_is_True(self):
        data = self.storage['test']
        data['key'] = 'value'
        self.assertTrue(data.is_changed)
