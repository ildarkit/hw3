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


if __name__ == "__main__":
    unittest.main()
