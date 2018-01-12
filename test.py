#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest

import api
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
        self.store = Store()
        # self.store.connect()

    def get_response(self, request):
        return api.method_handler({"body": request, "headers": self.headers}, self.context)

    def test_empty_request(self):
        _, code = self.get_response({})
        self.assertEqual(api.INVALID_REQUEST, code)

    def test_bad_char_attribute(self):
        attr = api.CharField(required=False, nullable=True)
        obj_exc = attr.validate(0)
        self.assertIsInstance(obj_exc, AttributeError)
        obj_exc = attr.validate(-1)
        self.assertIsInstance(obj_exc, AttributeError)

    def test_bad_arguments_attribute(self):
        attr = api.ArgumentsField(required=True, nullable=True)
        obj_exc = attr.validate(0)
        self.assertIsInstance(obj_exc, AttributeError)
        obj_exc = attr.validate(-1)
        self.assertIsInstance(obj_exc, AttributeError)
        obj_exc = attr.validate({1, })
        self.assertIsInstance(obj_exc, AttributeError)
        obj_exc = attr.validate('0')
        self.assertIsInstance(obj_exc, AttributeError)
        obj_exc = attr.validate('-1')
        self.assertIsInstance(obj_exc, AttributeError)

    def test_bad_email_attribute(self):
        attr = api.EmailField(required=False, nullable=True)
        obj_exc = attr.validate(0)
        self.assertIsInstance(obj_exc, AttributeError)
        obj_exc = attr.validate(-1)
        self.assertIsInstance(obj_exc, AttributeError)
        obj_exc = attr.validate('0')
        self.assertIsInstance(obj_exc, AttributeError)
        obj_exc = attr.validate('iuejh339 dl93')
        self.assertIsInstance(obj_exc, AttributeError)
        obj_exc = attr.validate([])
        self.assertIsInstance(obj_exc, AttributeError)

    def test_bad_phone_attribute(self):
        attr = api.PhoneField(required=False, nullable=True)
        obj_exc = attr.validate('737473dh321')
        self.assertIsInstance(obj_exc, AttributeError)
        obj_exc = attr.validate(0)
        self.assertIsInstance(obj_exc, AttributeError)
        obj_exc = attr.validate(-1)
        self.assertIsInstance(obj_exc, AttributeError)
        obj_exc = attr.validate('790000323732')
        self.assertIsInstance(obj_exc, AttributeError)

    def test_date_attribute(self):
        attr = api.DateField(required=False, nullable=True)
        obj_exc = attr.validate('01.')
        self.assertIsInstance(obj_exc, AttributeError)
        obj_exc = attr.validate(12122017)
        self.assertIsInstance(obj_exc, AttributeError)
        obj_exc = attr.validate(-1)
        self.assertIsInstance(obj_exc, AttributeError)
        obj_exc = attr.validate('32.12.2017')
        self.assertIsInstance(obj_exc, AttributeError)
        obj_exc = attr.validate('2017.12.31')
        self.assertIsInstance(obj_exc, AttributeError)
        obj_exc = attr.validate('12.01.17')
        self.assertIsInstance(obj_exc, AttributeError)
        obj_exc = attr.validate('10.01.200')
        self.assertIsInstance(obj_exc, AttributeError)
        obj_exc = attr.validate('..')
        self.assertIsInstance(obj_exc, AttributeError)
        obj_exc = attr.validate([])
        self.assertIsInstance(obj_exc, AttributeError)
        obj_exc = attr.validate(-0.0)
        self.assertIsInstance(obj_exc, AttributeError)

    def test_bad_birthday_attribute(self):
        attr = api.BirthDayField(required=False, nullable=True)
        obj_exc = attr.validate('01.')
        self.assertIsInstance(obj_exc, AttributeError)
        obj_exc = attr.validate(12122017)
        self.assertIsInstance(obj_exc, AttributeError)
        obj_exc = attr.validate(-1)
        self.assertIsInstance(obj_exc, AttributeError)
        obj_exc = attr.validate('32.12.2017')
        self.assertIsInstance(obj_exc, AttributeError)
        obj_exc = attr.validate('2017.12.31')
        self.assertIsInstance(obj_exc, AttributeError)
        obj_exc = attr.validate('12.01.17')
        self.assertIsInstance(obj_exc, AttributeError)
        obj_exc = attr.validate('10.01.200')
        self.assertIsInstance(obj_exc, AttributeError)
        obj_exc = attr.validate('..')
        self.assertIsInstance(obj_exc, AttributeError)
        obj_exc = attr.validate('01.01.1917')
        self.assertIsInstance(obj_exc, AttributeError)
        obj_exc = attr.validate([])
        self.assertIsInstance(obj_exc, AttributeError)
        obj_exc = attr.validate(-0.0)
        self.assertIsInstance(obj_exc, AttributeError)
        obj_exc = attr.validate('20.12.3018')
        self.assertIsInstance(obj_exc, AttributeError)

    def test_bad_gender_attribute(self):
        attr = api.GenderField(required=False, nullable=True)
        obj_exc = attr.validate([])
        self.assertIsInstance(obj_exc, AttributeError)
        obj_exc = attr.validate('1')
        self.assertIsInstance(obj_exc, AttributeError)
        obj_exc = attr.validate(1.0)
        self.assertIsInstance(obj_exc, AttributeError)
        obj_exc = attr.validate(-1)
        self.assertIsInstance(obj_exc, AttributeError)

    def test_bad_clientids_attribute(self):
        attr = api.ClientIDsField(required=True)
        obj_exc = attr.validate([0])
        self.assertIsInstance(obj_exc, AttributeError)
        obj_exc = attr.validate([-1])
        self.assertIsInstance(obj_exc, AttributeError)
        obj_exc = attr.validate([])
        self.assertIsInstance(obj_exc, AttributeError)
        obj_exc = attr.validate(-1)
        self.assertIsInstance(obj_exc, AttributeError)
        obj_exc = attr.validate(0)
        self.assertIsInstance(obj_exc, AttributeError)
        obj_exc = attr.validate(' ')
        self.assertIsInstance(obj_exc, AttributeError)
        obj_exc = attr.validate('[1, -1, 0]')
        self.assertIsInstance(obj_exc, AttributeError)
        obj_exc = attr.validate(-1.0)
        self.assertIsInstance(obj_exc, AttributeError)
        obj_exc = attr.validate([1.0, 2.0, 3.0])
        self.assertIsInstance(obj_exc, AttributeError)

    def test_required_attributes(self):
        attr = api.ClientIDsField(required=True)
        obj_exc = attr.validate(None)
        self.assertIsInstance(obj_exc, AttributeError)

        attr = api.GenderField(required=True, nullable=True)
        obj_exc = attr.validate(None)
        self.assertIsInstance(obj_exc, AttributeError)

        attr = api.BirthDayField(required=True, nullable=True)
        obj_exc = attr.validate(None)
        self.assertIsInstance(obj_exc, AttributeError)

        attr = api.DateField(required=True, nullable=True)
        obj_exc = attr.validate(None)
        self.assertIsInstance(obj_exc, AttributeError)

        attr = api.PhoneField(required=True, nullable=True)
        obj_exc = attr.validate(None)
        self.assertIsInstance(obj_exc, AttributeError)

        attr = api.EmailField(required=True, nullable=True)
        obj_exc = attr.validate(None)
        self.assertIsInstance(obj_exc, AttributeError)

        attr = api.ArgumentsField(required=True, nullable=True)
        obj_exc = attr.validate(None)
        self.assertIsInstance(obj_exc, AttributeError)

        attr = api.CharField(required=True, nullable=True)
        obj_exc = attr.validate(None)
        self.assertIsInstance(obj_exc, AttributeError)

    def test_nullable_attributes(self):
        attr = api.ClientIDsField(required=True)
        obj_exc = attr.validate('')
        self.assertIsInstance(obj_exc, AttributeError)

        attr = api.GenderField(required=True, nullable=False)
        obj_exc = attr.validate('')
        self.assertIsInstance(obj_exc, AttributeError)

        attr = api.BirthDayField(required=True, nullable=False)
        obj_exc = attr.validate('')
        self.assertIsInstance(obj_exc, AttributeError)

        attr = api.DateField(required=True, nullable=False)
        obj_exc = attr.validate('')
        self.assertIsInstance(obj_exc, AttributeError)

        attr = api.PhoneField(required=True, nullable=False)
        obj_exc = attr.validate('')
        self.assertIsInstance(obj_exc, AttributeError)

        attr = api.EmailField(required=True, nullable=False)
        obj_exc = attr.validate('')
        self.assertIsInstance(obj_exc, AttributeError)

        attr = api.ArgumentsField(required=True, nullable=False)
        obj_exc = attr.validate('')
        self.assertIsInstance(obj_exc, AttributeError)

        attr = api.CharField(required=True, nullable=False)
        obj_exc = attr.validate('')
        self.assertIsInstance(obj_exc, AttributeError)

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
        key = "uid:c20ad4d76fe97759aa27a0c99bff6710"
        value = self.store.cache_get(key) or -1
        self.assertEqual(value, 1)  # in first time may fail. try again?

        key = "uid:123"
        value = self.store.cache_get(key) or -1
        self.assertEqual(value, -1)

    def test_on_connected_store_get(self):
        key = "uid:c20ad4d76fe97759aa27a0c99bff6710"
        value = self.store.get(key)
        self.assertEqual(value, 1)

    @cases([{"account": "horns&hoofs", "login": "h&f", "method": "online_score", "token": "", "arguments": {}},
            {"account": "ой", "login": "h&f", "method": "online_score", "token": "sdd", "arguments": {}},
            {"account": "horns&hoofs", "login": "admin", "method": "online_score", "token": "ой", "arguments": {}},
            {"account": "", "login": "admin", "method": "online_score", "token": "", "arguments": {}},
            {"account": "horns&hoofs", "login": "admin", "method": "online_score", "token": "", "arguments": {}},
            {"account": "horns&hoofs", "login": "ой", "method": "online_score", "token": "", "arguments": {}}])
    def test_bad_auth(self, request):
        request = api.set_attributes(api.MethodRequest, request)
        self.assertFalse(api.check_auth(request))

    def test_set_attributes(self):
        request = {"account": "Ой", "login": "", "method": "метод",
                   "token": "что-то", "arguments": {'аргумент': 'значение'}
                   }
        request = api.set_attributes(api.MethodRequest, request)
        self.assertEqual(request.account, 'Ой')
        self.assertEqual(request.login, '')
        self.assertEqual(request.method, 'метод')
        self.assertEqual(request.token, 'что-то')
        self.assertEqual(request.arguments, {'аргумент': 'значение'})

        kwargs = {'date': '20.07.2017', 'client_ids': [1, 2, 3, 4]}
        request = api.set_attributes(api.ClientsInterestsRequest, kwargs)
        self.assertEqual(request.date, '20.07.2017')
        self.assertEqual(request.client_ids, [1, 2, 3, 4])

        kwargs = {'first_name': 'имя', 'last_name': 'фамилия', 'gender': 1, 'phone': '79175002040',
                  'birthday': '01.01.1990', 'email': 'имя@domain.com'
                  }
        request = api.set_attributes(api.OnlineScoreRequest, kwargs)
        self.assertEqual(request.first_name, 'имя')
        self.assertEqual(request.last_name, 'фамилия')
        self.assertEqual(request.gender, 1)
        self.assertEqual(request.phone, '79175002040')
        self.assertEqual(request.birthday, '01.01.1990')
        self.assertEqual(request.email, 'имя@domain.com')


if __name__ == "__main__":
    unittest.main()
