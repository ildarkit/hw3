import unittest

import api
from store import Store


class TestSuite(unittest.TestCase):
    def setUp(self):
        self.context = {'request_id': 0}
        self.headers = {}
        self.store = Store()

    def get_response(self, request):
        return api.method_handler({"body": request, "headers": self.headers}, self.context, self.store)

    def test_empty_request(self):
        _, code = self.get_response({})
        self.assertEqual(api.INVALID_REQUEST, code)

    def test_char_field(self):
        field = api.CharField(required=False, nullable=True)
        field = ''

    def test_arguments_field(self):
        field = api.ArgumentsField(required=True, nullable=True)
        field = ''

    def test_email_field(self):
        field = api.EmailField(required=False, nullable=True)
        field = ''

    def test_phone_field(self):
        field = api.PhoneField(required=False, nullable=True)
        field = ''

    def test_date_field(self):
        field = api.DateField(required=False, nullable=True)
        field = ''

    def test_birthday_field(self):
        field = api.BirthDayField(required=False, nullable=True)
        field = ''

    def test_gender_field(self):
        field = api.GenderField(required=False, nullable=True)
        field = ''

    def test_clients_field(self):
        field = api.ClientIDsField(required=True)
        obj_exc = field.validate(None)
        self.assertIsInstance(obj_exc, str)
        obj_exc = field.validate(0)
        self.assertIsInstance(obj_exc, str)
        result = field.validate(-1)
        self.assertTrue(obj_exc)
        obj_exc = field.validate('')
        self.assertIsInstance(obj_exc, str)



if __name__ == "__main__":
    unittest.main()
