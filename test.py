#!/usr/bin/env python
# -*- coding: utf-8 -*-

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

    @cases([{'value': 0, 'error': api.TypeAttributeError},
            {'value': -1, 'error': api.TypeAttributeError},
            {'value': [], 'error': api.TypeAttributeError}])
    def test_bad_char_attribute(self, kwargs):
        attr = api.CharField(required=False, nullable=True)
        obj_exc = attr.validate(kwargs['value'])
        self.assertIsInstance(obj_exc, kwargs['error'])

    @cases([{'value': 0, 'error': api.TypeAttributeError},
            {'value': -1, 'error': api.TypeAttributeError},
            {'value': {1, }, 'error': api.TypeAttributeError},
            {'value': '0', 'error': api.TypeAttributeError},
            {'value': '-1', 'error': api.TypeAttributeError}])
    def test_bad_arguments_attribute(self, kwargs):
        attr = api.ArgumentsField(required=True, nullable=True)
        obj_exc = attr.validate(kwargs['value'])
        self.assertIsInstance(obj_exc, kwargs['error'])

    @cases([{'value': 0, 'error': api.TypeAttributeError},
            {'value': -1, 'error': api.TypeAttributeError},
            {'value': '0', 'error': api.InvalidAttributeError},
            {'value': 'iuejh339 dl93', 'error': api.InvalidAttributeError},
            {'value': [], 'error': api.TypeAttributeError}])
    def test_bad_email_attribute(self, kwargs):
        attr = api.EmailField(required=False, nullable=True)
        obj_exc = attr.validate(kwargs['value'])
        self.assertIsInstance(obj_exc, kwargs['error'])

    @cases([{'value': '737473dh321', 'error': api.InvalidAttributeError},
            {'value': 0, 'error': api.TypeAttributeError},
            {'value': -1, 'error': api.TypeAttributeError},
            {'value': '790000323732', 'error': api.InvalidAttributeError}])
    def test_bad_phone_attribute(self, kwargs):
        attr = api.PhoneField(required=False, nullable=True)
        obj_exc = attr.validate(kwargs['value'])
        self.assertIsInstance(obj_exc, kwargs['error'])

    @cases([{'value': '01.', 'error': api.InvalidAttributeError},
            {'value': 12122017, 'error': api.TypeAttributeError},
            {'value': -1, 'error': api.TypeAttributeError},
            {'value': '32.12.2017', 'error': api.InvalidAttributeError},
            {'value': '2017.12.31', 'error': api.InvalidAttributeError},
            {'value': '12.01.17', 'error': api.InvalidAttributeError},
            {'value': '10.01.200', 'error': api.InvalidAttributeError},
            {'value': '..', 'error': api.InvalidAttributeError},
            {'value': [], 'error': api.TypeAttributeError},
            {'value': -0.0, 'error': api.TypeAttributeError}])
    def test_bad_date_attribute(self, kwargs):
        attr = api.DateField(required=False, nullable=True)
        obj_exc = attr.validate(kwargs['value'])
        self.assertIsInstance(obj_exc, kwargs['error'])

    @cases([{'value': '01.', 'error': api.InvalidAttributeError},
            {'value': 12122017, 'error': api.TypeAttributeError},
            {'value': -1, 'error': api.TypeAttributeError},
            {'value': '32.12.2017', 'error': api.InvalidAttributeError},
            {'value': '2017.12.31', 'error': api.InvalidAttributeError},
            {'value': '12.01.17', 'error': api.InvalidAttributeError},
            {'value': '10.01.200', 'error': api.InvalidAttributeError},
            {'value': '..', 'error': api.InvalidAttributeError},
            {'value': [], 'error': api.TypeAttributeError},
            {'value': -0.0, 'error': api.TypeAttributeError},
            {'value': '01.01.1917', 'error': api.InvalidAttributeError},
            {'value': '20.12.3018', 'error': api.InvalidAttributeError}])
    def test_bad_birthday_attribute(self, kwargs):
        attr = api.BirthDayField(required=False, nullable=True)
        obj_exc = attr.validate(kwargs['value'])
        self.assertIsInstance(obj_exc, kwargs['error'])

    @cases([{'value': '1', 'error': api.TypeAttributeError},
            {'value': 1.0, 'error': api.TypeAttributeError},
            {'value': -1, 'error': api.InvalidAttributeError},
            {'value': 7, 'error': api.InvalidAttributeError},
            {'value': -2.0, 'error': api.TypeAttributeError},
            {'value': [], 'error': api.TypeAttributeError},
            {'value': -0.0, 'error': api.TypeAttributeError}])
    def test_bad_gender_attribute(self, kwargs):
        attr = api.GenderField(required=False, nullable=True)
        obj_exc = attr.validate(kwargs['value'])
        self.assertIsInstance(obj_exc, kwargs['error'])

    @cases([{'value': [0], 'error': api.InvalidAttributeError},
            {'value': [-1], 'error': api.InvalidAttributeError},
            {'value': -1, 'error': api.TypeAttributeError},
            {'value': 0, 'error': api.TypeAttributeError},
            {'value': ' ', 'error': api.TypeAttributeError},
            {'value': '[1, -1, 0]', 'error': api.TypeAttributeError},
            {'value': -1.0, 'error': api.TypeAttributeError},
            {'value': [1.0, 2.0, 3.0], 'error': api.InvalidAttributeError}])
    def test_bad_clientids_attribute(self, kwargs):
        attr = api.ClientIDsField(required=True)
        obj_exc = attr.validate(kwargs['value'])
        self.assertIsInstance(obj_exc, kwargs['error'])

    @cases([{'attr': api.ClientIDsField(required=True)},
            {'attr': api.GenderField(required=True, nullable=True)},
            {'attr': api.BirthDayField(required=True, nullable=True)},
            {'attr': api.DateField(required=True, nullable=True)},
            {'attr': api.PhoneField(required=True, nullable=True)},
            {'attr': api.EmailField(required=True, nullable=True)},
            {'attr': api.ArgumentsField(required=True, nullable=True)},
            {'attr': api.CharField(required=True, nullable=True)}])
    def test_required_attributes(self, kwargs):
        attr = kwargs['attr']
        obj_exc = attr.validate(None)
        self.assertIsInstance(obj_exc, api.RequiredAttributeError)

    @cases([{'attr': api.ClientIDsField(required=True)},
            {'attr': api.GenderField(required=True, nullable=False)},
            {'attr': api.BirthDayField(required=True, nullable=False)},
            {'attr': api.DateField(required=True, nullable=False)},
            {'attr': api.PhoneField(required=True, nullable=False)},
            {'attr': api.EmailField(required=True, nullable=False)},
            {'attr': api.ArgumentsField(required=True, nullable=False)},
            {'attr': api.CharField(required=True, nullable=False)}])
    def test_nullable_attributes(self, kwargs):
        attr = kwargs['attr']
        obj_exc = attr.validate('')
        self.assertIsInstance(obj_exc, api.NotNullableAttributeError)

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


class StoreTest(unittest.TestCase):
    def setUp(self):
        self.store = Store(attempts=3)
        self.store.connect()

    def test_on_disconnected_store_cache_set_cache_get(self):
        self.store = Store(port=9000, connect_timeout=1)

        key = "uid:c20ad4d76fe97759aa27a0c99bff6710"
        self.store.cache_set(key, -1, 60)
        value = self.store.cache_get(key) or 0
        self.assertEqual(value, 0)

        self.store.cache_set(key, 0, 60)
        value = self.store.cache_get(key) or 1
        self.assertEqual(value, 1)

    def test_on_connected_store_cache_set_cache_get(self):
        key = "uid:123"
        self.store.cache_set(key, 9999, 1)
        value = self.store.cache_get(key) or 0
        self.assertEqual(value, 9999)

        key = "uid:c20ad4d76fe97759aa27a0c99bff6710"
        self.store.cache_set(key, 1, 60 * 60)
        value = self.store.cache_get(key) or -1
        self.assertEqual(value, 1)

    def test_on_connected_store_cache_get(self):
        key = "uid:123"
        value = self.store.cache_get(key) or -1
        self.assertEqual(value, -1)

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
        self.store.redis.set('uid:9a423ca46b5c7d79f8d335405e273261', 13.7)
        self.store.redis.set('uid:99e176a6339c3ed7d753d610e2580f01', -0.9)
        self.assertAlmostEqual(scoring.get_score(self.store, **kwargs), score, delta=0.1)


if __name__ == "__main__":
    unittest.main()
