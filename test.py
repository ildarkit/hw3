#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket
import unittest

import api
import scoring
from store import Store


def cases(test_cases):
    def decorator(method):
        def wrapper(self):
            for test in test_cases:
                method(self, test)

        return wrapper

    return decorator


class TestSuite(unittest.TestCase):
    def setUp(self):
        self.context = {'request_id': 0}
        self.headers = {}

    def get_response(self, request):
        return api.method_handler({"body": request, "headers": self.headers}, self.context)

    def test_empty_request(self):
        _, code = self.get_response({})
        self.assertEqual(api.INVALID_REQUEST, code)

    @cases([0, -1, []])
    def test_bad_char_attribute(self, value):
        attr = api.CharField(required=False, nullable=True)
        self.assertFalse(attr.validate(value))

    @cases([0, -1, {1, }, '0', '-1'])
    def test_bad_arguments_attribute(self, value):
        attr = api.ArgumentsField(required=True, nullable=True)
        self.assertFalse(attr.validate(value))

    @cases([0, -1, '0', 'iuejh339 dl93', []])
    def test_bad_email_attribute(self, value):
        attr = api.EmailField(required=False, nullable=True)
        self.assertFalse(attr.validate(value))

    @cases(['737473dh321', 0, -1, '790000323732'])
    def test_bad_phone_attribute(self, value):
        attr = api.PhoneField(required=False, nullable=True)
        self.assertFalse(attr.validate(value))

    @cases(['01.', 12122017, -1, '32.12.2017', '2017.12.31',
            '12.01.17', '10.01.200', '..', [], -0.0])
    def test_bad_date_attribute(self, value):
        attr = api.DateField(required=False, nullable=True)
        self.assertFalse(attr.validate(value))

    @cases(['01.', 12122017, -1, '32.12.2017', '2017.12.31',
            '12.01.17', '10.01.200', '..', [], -0.0, '01.01.1917',
            '20.12.3018'])
    def test_bad_birthday_attribute(self, value):
        attr = api.BirthDayField(required=False, nullable=True)
        self.assertFalse(attr.validate(value))

    @cases(['1', 1.0, -1, 7, -2.0, [], -0.0])
    def test_bad_gender_attribute(self, value):
        attr = api.GenderField(required=False, nullable=True)
        self.assertFalse(attr.validate(value))

    @cases([[0], [-1], -1, 0, ' ', '[1, -1, 0]', -1.0,
            [1.0, 2.0, 3.0]])
    def test_bad_clientids_attribute(self, value):
        attr = api.ClientIDsField(required=True)
        self.assertFalse(attr.validate(value))

    @cases([api.ClientIDsField(required=True),
            api.GenderField(required=True, nullable=True),
            api.BirthDayField(required=True, nullable=True),
            api.DateField(required=True, nullable=True),
            api.PhoneField(required=True, nullable=True),
            api.EmailField(required=True, nullable=True),
            api.ArgumentsField(required=True, nullable=True),
            api.CharField(required=True, nullable=True)])
    def test_required_attributes(self, value):
        self.assertFalse(value.validate(None))

    @cases([api.ClientIDsField(required=True),
            api.GenderField(required=True, nullable=False),
            api.BirthDayField(required=True, nullable=False),
            api.DateField(required=True, nullable=False),
            api.PhoneField(required=True, nullable=False),
            api.EmailField(required=True, nullable=False),
            api.ArgumentsField(required=True, nullable=False),
            api.CharField(required=True, nullable=False)])
    def test_nullable_attributes(self, value):
        self.assertFalse(value.validate(''))

    @cases([{"account": "horns&hoofs", "login": "h&f", "method": "online_score", "token": "", "arguments": {}},
            {"account": "ой", "login": "h&f", "method": "online_score", "token": "sdd", "arguments": {}},
            {"account": "horns&hoofs", "login": "admin", "method": "online_score", "token": "ой", "arguments": {}},
            {"account": "", "login": "admin", "method": "online_score", "token": "", "arguments": {}},
            {"account": "horns&hoofs", "login": "admin", "method": "online_score", "token": "", "arguments": {}},
            {"account": "horns&hoofs", "login": "ой", "method": "online_score", "token": "", "arguments": {}}])
    def test_bad_auth(self, request):
        request = api.set_attributes(api.MethodRequest, request)
        self.assertFalse(api.check_auth(request))

    @cases([{'test_class': api.MethodRequest,
             'values': {"account": "Ой", "login": "", "method": "метод",
                        "token": "что-то", "arguments": {'аргумент': 'значение'}}},
            {'test_class': api.ClientsInterestsRequest,
             'values': {'date': '20.07.2017', 'client_ids': [1, 2, 3, 4]}},
            {'test_class': api.OnlineScoreRequest,
             'values': {'first_name': 'имя', 'last_name': 'фамилия', 'gender': 1, 'phone': '79175002040',
                        'birthday': '01.01.1990', 'email': 'имя@domain.com'}}
            ])
    def test_set_attributes(self, kwargs):

        filled_obj = api.set_attributes(kwargs['test_class'], kwargs['values'])
        for attr, value in kwargs['values'].items():
            self.assertEqual(filled_obj.__dict__[attr].__dict__['value'], value)


def has_storage():
    result = False
    try:
        store = Store(connect_timeout=2, attempts=2)
        store.connect()
        result = True
    except socket.error:
        pass
    return result


flag_has_storage = has_storage()


@unittest.skipUnless(flag_has_storage, 'Storage tests are skipping')
class StorageTest(unittest.TestCase):
    def setUp(self):
        self.store = Store(connect_timeout=5, attempts=3)

    def test_on_disconnected_store_cache_set_cache_get(self):
        self.store = Store(port=9999, connect_timeout=1, attempts=1)

        key = "uid:c20ad4d76fe97759aa27a0c99bff6710"
        self.store.cache_set(key, -1, 60)
        value = self.store.cache_get(key) or 0
        self.assertEqual(value, 0)

    @cases([{'key': "uid:123456", 'value': 1},
            {'key': "uid:123456", 'value': -3.7}])
    def test_on_connected_store_get_cache_get(self, kwargs):
        self.store.connect()

        key = kwargs['key']
        self.store.cache_set(key, kwargs['value'], 60 * 60)
        value = self.store.cache_get(key) or 0
        self.assertEqual(value, kwargs['value'])

    @cases([{'key': "uid:654321", 'value': 'books'},
            {'key': "uid:654321", 'value': 'путешествие'}])
    def test_on_connected_store_get(self, kwargs):
        self.store.connect()

        key = kwargs['key']
        self.store.redis.delete(key)
        self.store.redis.rpush(key, kwargs['value'])
        value = self.store.get(key) or None
        self.assertEqual(value, [kwargs['value']])


class ScoringTest(unittest.TestCase):
    def setUp(self):
        self.store = Store(connect_timeout=5, attempts=3)

    @unittest.skipUnless(flag_has_storage, 'Skipping get_interests cases')
    @cases([{'user_id': 1, 'interest1': 'books', 'interest2': 'cinema'},
            {'user_id': 2, 'interest1': 'music', 'interest2': 'travel'},
            {'user_id': 3, 'interest1': 'sport', 'interest2': 'tv'},
            {'user_id': 4, 'interest1': 'photography', 'interest2': 'tourism'}])
    def test_on_connected_store_set_get_interests(self, user_interest):
        key = 'i:{}'.format(user_interest['user_id'])
        self.store.redis.delete(key)
        self.store.redis.rpush(key, user_interest['interest1'])
        self.store.redis.rpush(key, user_interest['interest2'])
        self.assertEqual(
            scoring.get_interests(self.store, user_interest['user_id']),
            [user_interest['interest1'], user_interest['interest2']]
        )

    @unittest.skipUnless(flag_has_storage, 'Skipping get_score cases')
    @cases([{'first_name': 'ILDAR', 'last_name': 'Shamiev', 'gender': 1, 'phone': '', 'birthday': '01.01.1990',
             'email': 'имя@domain.com', 'score': 3.5},
            {'first_name': 'NAME', 'last_name': 'LAST', 'gender': 0, 'phone': '', 'birthday': '01.01.1980',
             'email': 'имя@domain.com', 'score': 13.7},
            {'first_name': '', 'last_name': '', 'gender': 0, 'phone': '79175002040', 'birthday': '06.01.2000',
             'email': '', 'score': 3.0},
            {'first_name': 'Name', 'last_name': 'name', 'gender': 1, 'phone': '', 'birthday': '13.01.1999',
             'email': '', 'score': -0.9}])
    def test_on_connected_store_get_score(self, kwargs):
        score = kwargs.pop('score')
        kwargs['birthday'] = api.DateField.str_to_date(kwargs['birthday'])
        self.store.cache_set('uid:9a423ca46b5c7d79f8d335405e273261', 13.7, 60 * 60)
        self.store.cache_set('uid:99e176a6339c3ed7d753d610e2580f01', -0.9, 60 * 60)
        self.assertAlmostEqual(scoring.get_score(self.store, **kwargs), score, delta=0.1)

    @unittest.expectedFailure
    def test_on_disconnected_store_get_interests(self):
        self.store = Store(port=9999, connect_timeout=1, attempts=2)
        self.assertRaises(socket.timeout, scoring.get_interests(self.store, '12345'))

    @cases([{'first_name': 'ILDAR', 'last_name': 'Shamiev', 'gender': 1, 'phone': '', 'birthday': '01.01.1990',
             'email': 'имя@domain.com', 'score': 3.5}])
    def test_on_disconnected_store_get_score(self, kwargs):
        self.store = Store(port=9999, connect_timeout=1, attempts=1)
        score = kwargs.pop('score')
        kwargs['birthday'] = api.DateField.str_to_date(kwargs['birthday'])
        self.assertAlmostEqual(scoring.get_score(self.store, **kwargs), score, delta=0.1)


if __name__ == "__main__":
    unittest.main()
