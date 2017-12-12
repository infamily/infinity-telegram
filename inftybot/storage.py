# coding: utf-8
import boto3
from werkzeug.utils import import_string

storage_registry = []


def get_dynamodb():
    """Returns dynamodb resource"""
    return boto3.resource('dynamodb')


def create_table(resource, table_name, key_schema, attribute_definitions, provisioned_throughput):
    """Creates dynamodb table"""
    return resource.create_table(
        TableName=table_name,
        KeySchema=key_schema,
        AttributeDefinitions=attribute_definitions,
        ProvisionedThroughput=provisioned_throughput
    )


def describe_table(client, table_name):
    """Return table description"""
    return client.describe_table(TableName=table_name)


def register_storage(cls):
    """Adds storage class to the registry"""
    storage_registry.append(cls)


def create_tables(registry):
    """Creates tables for tables from registry"""
    for storage_cls in registry:
        if isinstance(storage_cls, str):
            storage_cls = import_string(storage_cls)
        storage_cls().create_table()


def drop_tables(registry):
    """Drops tables (from registry)"""
    for storage_cls in registry:
        if isinstance(storage_cls, str):
            storage_cls = import_string(storage_cls)
        storage_cls().delete_table()


class StorageData(object):
    """
    Object that behaves like a dict but it is possible to trigger update data in the DynamoDB the following methods:
        * call store() directly
        * on the object's native __del__ stage
    """
    def __init__(self, storage, key, data=None):
        self._storage = storage
        self._key = key
        self._data = data or {}
        self.is_changed = False

    def __getitem__(self, item):
        return self._data[item]

    def __setitem__(self, key, value):
        """Updates the data and marks object is_changed is True"""
        self.is_changed = True
        self._data[key] = value

    def __delitem__(self, key):
        """Removes key from the data and marks object is_changed is True"""
        self.is_changed = True
        del self._data[key]

    def __iter__(self):
        """Needed to dict() casting"""
        return iter(self._data.items())

    def __del__(self):
        """Every deletion it will trigger store() method"""
        self.store()

    def __bool__(self):
        """Check that there is no data"""
        return bool(self._data)

    def get(self, item, default=None):
        return self._data.get(item, default)

    def store(self, force=False):
        """Handle data saving (when is_changed or forced)"""
        if self.is_changed or force:
            self._storage.update(self._key, self._data)


class DynamoDBStorage(object):
    """Base class for storages"""
    table_name = None
    key_schema = None
    attribute_definitions = None
    provisioned_throughput = None

    data_key = None
    data_default_value = {}

    query_key_coerce = str

    def __init__(self, resource=None):
        if not resource:
            resource = get_dynamodb()

        self._resource = resource
        self._client = self._resource.meta.client
        self._table = self._resource.Table(self.table_name)

    def create_table(self):
        """Creates table for current storage"""
        return create_table(
            self._resource,
            table_name=self.table_name,
            key_schema=self.key_schema,
            attribute_definitions=self.attribute_definitions,
            provisioned_throughput=self.provisioned_throughput
        )

    def describe_table(self):
        """Describe current storage table"""
        response = describe_table(self._client, table_name=self.table_name)
        return response.get('Table')

    def delete_table(self):
        """Delete table of the current storage"""
        return self._table.delete()

    def get_primary_key(self):
        """Returns primary key for proper querying"""
        return self.key_schema[0]['AttributeName']

    def get_query_key(self, key):
        """Returns query_key for proper querying"""
        pk_attr = self.get_primary_key()
        return {
            pk_attr: self.query_key_coerce(key)
        }

    def process_data(self, key, item):
        """Makes StorageData from the plain dict object"""
        return StorageData(self, key, item)

    def get(self, key):
        """Retrieve single item by key"""
        response = self._table.get_item(Key=key)
        item = response.get('Item', {})
        data = item.get(self.data_key, self.data_default_value)
        return self.process_data(key, data)

    def insert(self, obj):
        """
        Not implemented. Actually no needed, but
        ```self._table.put_item(Item=obj)``` may be used for
        """
        raise NotImplemented

    def update(self, key, obj):
        """Update single item in the DB"""
        data = dict(obj)
        response = self._table.update_item(
            Key=key,
            UpdateExpression='SET {}=:data'.format(self.data_key),
            ExpressionAttributeValues={':data': data},
        )
        return response.get('ResponseMetadata', {}).get('HTTPStatusCode', -1) == 200

    def delete(self, key):
        """Delete single item from the DB"""
        response = self._table.delete_item(Key=key)
        return response.get('ResponseMetadata', {}).get('HTTPStatusCode', -1) == 200

    def __getitem__(self, item):
        """Makes possible to call ```storage[user_id]```"""
        key = self.get_query_key(item)
        return self.get(key)

    def __setitem__(self, item, value):
        """Makes possible to set ```storage[user_id]=data```"""
        key = self.get_query_key(item)
        return self.update(key, value)

    def __delitem__(self, key):
        """Makes possible to delete the whole object ```del storage[user_id]```"""
        key = self.get_query_key(key)
        return self.delete(key)


class UserDataStorage(DynamoDBStorage):
    """Storage for dispatcher's user_data"""
    table_name = 'users'
    data_key = 'user_data'
    key_schema = [
        {
            'AttributeName': 'user_id',
            'KeyType': 'HASH'
        },
    ]
    attribute_definitions = [
        {
            'AttributeName': 'user_id',
            'AttributeType': 'S'
        },
    ]
    provisioned_throughput = {
        # todo
        'ReadCapacityUnits': 5,
        'WriteCapacityUnits': 5,
    }


class ChatDataStorage(DynamoDBStorage):
    """Storage for dispatcher's chat_data"""
    table_name = 'chats'
    data_key = 'chat_data'
    key_schema = [
        {
            'AttributeName': 'chat_id',
            'KeyType': 'HASH'
        },
    ]
    attribute_definitions = [
        {
            'AttributeName': 'chat_id',
            'AttributeType': 'S'
        },
    ]
    provisioned_throughput = {
        # todo
        'ReadCapacityUnits': 5,
        'WriteCapacityUnits': 5,
    }


register_storage(UserDataStorage)
register_storage(ChatDataStorage)
__all__ = ['UserDataStorage', 'ChatDataStorage']
