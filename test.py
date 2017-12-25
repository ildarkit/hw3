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
        obj_exc = field.validate('01.')
        self.assertIsInstance(obj_exc, AttributeError)
        obj_exc = field.validate(12122017)
        self.assertIsInstance(obj_exc, AttributeError)
        obj_exc = field.validate(-1)
        self.assertIsInstance(obj_exc, AttributeError)
        obj_exc = field.validate('32.12.2017')
        self.assertIsInstance(obj_exc, AttributeError)
        obj_exc = field.validate('2017.12.31')
        self.assertIsInstance(obj_exc, AttributeError)
        obj_exc = field.validate('12.01.17')
        self.assertIsInstance(obj_exc, AttributeError)
        obj_exc = field.validate('10.01.200')
        self.assertIsInstance(obj_exc, AttributeError)
        obj_exc = field.validate('..')
        self.assertIsInstance(obj_exc, AttributeError)
        obj_exc = field.validate([])
        self.assertIsInstance(obj_exc, AttributeError)
        obj_exc = field.validate(-0.0)
        self.assertIsInstance(obj_exc, AttributeError)

    def test_bad_birthday_field(self):
        field = api.BirthDayField(required=False, nullable=True)
        obj_exc = field.validate('01.')
        self.assertIsInstance(obj_exc, AttributeError)
        obj_exc = field.validate(12122017)
        self.assertIsInstance(obj_exc, AttributeError)
        obj_exc = field.validate(-1)
        self.assertIsInstance(obj_exc, AttributeError)
        obj_exc = field.validate('32.12.2017')
        self.assertIsInstance(obj_exc, AttributeError)
        obj_exc = field.validate('2017.12.31')
        self.assertIsInstance(obj_exc, AttributeError)
        obj_exc = field.validate('12.01.17')
        self.assertIsInstance(obj_exc, AttributeError)
        obj_exc = field.validate('10.01.200')
        self.assertIsInstance(obj_exc, AttributeError)
        obj_exc = field.validate('..')
        self.assertIsInstance(obj_exc, AttributeError)
        obj_exc = field.validate('01.01.1917')
        self.assertIsInstance(obj_exc, AttributeError)
        obj_exc = field.validate([])
        self.assertIsInstance(obj_exc, AttributeError)
        obj_exc = field.validate(-0.0)
        self.assertIsInstance(obj_exc, AttributeError)
        obj_exc = field.validate('20.12.3018')
        self.assertIsInstance(obj_exc, AttributeError)

    def test_bad_gender_field(self):
        field = api.GenderField(required=False, nullable=True)
        obj_exc = field.validate([])
        self.assertIsInstance(obj_exc, AttributeError)
        obj_exc = field.validate('1')
        self.assertIsInstance(obj_exc, AttributeError)
        obj_exc = field.validate(1.0)
        self.assertIsInstance(obj_exc, AttributeError)
        obj_exc = field.validate(-1)
        self.assertIsInstance(obj_exc, AttributeError)

    def test_bad_clientids_field(self):
        field = api.ClientIDsField(required=True)
        obj_exc = field.validate([0])
        self.assertIsInstance(obj_exc, AttributeError)
        obj_exc = field.validate([-1])
        self.assertIsInstance(obj_exc, AttributeError)
        obj_exc = field.validate([])
        self.assertIsInstance(obj_exc, AttributeError)
        obj_exc = field.validate(-1)
        self.assertIsInstance(obj_exc, AttributeError)
        obj_exc = field.validate(0)
        self.assertIsInstance(obj_exc, AttributeError)
        obj_exc = field.validate(' ')
        self.assertIsInstance(obj_exc, AttributeError)
        obj_exc = field.validate('[1, -1, 0]')
        self.assertIsInstance(obj_exc, AttributeError)
        obj_exc = field.validate(-1.0)
        self.assertIsInstance(obj_exc, AttributeError)
        obj_exc = field.validate([1.0, 2.0, 3.0])
        self.assertIsInstance(obj_exc, AttributeError)

    def test_required_fields(self):
        field = api.ClientIDsField(required=True)
        obj_exc = field.validate(None)
        self.assertIsInstance(obj_exc, AttributeError)

        field = api.GenderField(required=True, nullable=True)
        obj_exc = field.validate(None)
        self.assertIsInstance(obj_exc, AttributeError)

        field = api.BirthDayField(required=True, nullable=True)
        obj_exc = field.validate(None)
        self.assertIsInstance(obj_exc, AttributeError)

        field = api.DateField(required=True, nullable=True)
        obj_exc = field.validate(None)
        self.assertIsInstance(obj_exc, AttributeError)

        field = api.PhoneField(required=True, nullable=True)
        obj_exc = field.validate(None)
        self.assertIsInstance(obj_exc, AttributeError)

        field = api.EmailField(required=True, nullable=True)
        obj_exc = field.validate(None)
        self.assertIsInstance(obj_exc, AttributeError)

        field = api.ArgumentsField(required=True, nullable=True)
        obj_exc = field.validate(None)
        self.assertIsInstance(obj_exc, AttributeError)

        field = api.CharField(required=True, nullable=True)
        obj_exc = field.validate(None)
        self.assertIsInstance(obj_exc, AttributeError)

    def test_nullable_fields(self):
        field = api.ClientIDsField(required=True)
        obj_exc = field.validate('')
        self.assertIsInstance(obj_exc, AttributeError)

        field = api.GenderField(required=True, nullable=False)
        obj_exc = field.validate('')
        self.assertIsInstance(obj_exc, AttributeError)

        field = api.BirthDayField(required=True, nullable=False)
        obj_exc = field.validate('')
        self.assertIsInstance(obj_exc, AttributeError)

        field = api.DateField(required=True, nullable=False)
        obj_exc = field.validate('')
        self.assertIsInstance(obj_exc, AttributeError)

        field = api.PhoneField(required=True, nullable=False)
        obj_exc = field.validate('')
        self.assertIsInstance(obj_exc, AttributeError)

        field = api.EmailField(required=True, nullable=False)
        obj_exc = field.validate('')
        self.assertIsInstance(obj_exc, AttributeError)

        field = api.ArgumentsField(required=True, nullable=False)
        obj_exc = field.validate('')
        self.assertIsInstance(obj_exc, AttributeError)

        field = api.CharField(required=True, nullable=False)
        obj_exc = field.validate('')
        self.assertIsInstance(obj_exc, AttributeError)


if __name__ == "__main__":
    unittest.main()
