#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import uuid
import logging
import hashlib
import datetime
from optparse import OptionParser
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler

from store import Store
from scoring import get_score
from scoring import get_interests

SALT = "Otus"
ADMIN_LOGIN = "admin"
ADMIN_SALT = "42"
OK = 200
BAD_REQUEST = 400
FORBIDDEN = 403
NOT_FOUND = 404
INVALID_REQUEST = 422
INTERNAL_ERROR = 500
ERRORS = {
    BAD_REQUEST: "Bad Request",
    FORBIDDEN: "Forbidden",
    NOT_FOUND: "Not Found",
    INVALID_REQUEST: "Invalid Request",
    INTERNAL_ERROR: "Internal Server Error",
}
UNKNOWN = 0
MALE = 1
FEMALE = 2
GENDERS = {
    UNKNOWN: "unknown",
    MALE: "male",
    FEMALE: "female",
}
STR_TYPE = unicode if hasattr(__builtins__, 'unicode') else str


class DeclarativeMeta(type):

    def __setattr__(cls, attr, value):
        try:
            result = None
            attribute = cls.__dict__[attr]
            if hasattr(attribute, 'validate'):
                result = attribute.validate(value)
            if isinstance(result, AttributeError):
                raise AttributeError(result.message.format(cls.__name__, attr))
            elif result:
                cls.__dict__[attr].value = value
        except KeyError:
            pass


class FieldBase(object):

    def __init__(self, required, nullable):
        self.required = required
        self.nullable = nullable

    def validate(self, value):
        if self.required and value is None:
            return AttributeError('{}: attribute <{}> is required')
        if not (value or self.nullable) and isinstance(value, self.instance):
            return AttributeError('{}: attribute <{}> is not nullable')
        return self._error_message(value) if not isinstance(value, self.instance) else True

    def __get__(self, instance, owner):
        if hasattr(self, 'value'):
            return self.value

    @staticmethod
    def _error_message(value):
        return AttributeError('{}: invalid value <{}> for attribute <{}>'.format('{}', value, '{}'))


class CharField(FieldBase):

    def __init__(self, required, nullable):
        self.instance = STR_TYPE
        super(CharField, self).__init__(required, nullable)


class ArgumentsField(FieldBase):
    def __init__(self, required, nullable):
        self.instance = dict
        super(ArgumentsField, self).__init__(required, nullable)


class EmailField(CharField):
    def __init__(self, required, nullable):
        super(EmailField, self).__init__(required, nullable)

    def validate(self, value):
        result = super(CharField, self).validate(value)
        if result is True:
            result = result if '@' in value else self._error_message(value)
        return result


class PhoneField(FieldBase):

    def __init__(self, required, nullable):
        self.instance = STR_TYPE
        super(PhoneField, self).__init__(required, nullable)

    def validate(self, value):
        result = self._error_message(value)
        try:
            if value:
                int(value)
        except ValueError:
            pass
        else:
            result = super(PhoneField, self).validate(value)
            if result is True and len(value) == 11 and value[0] == '7':
                return result
        return result


class DateField(FieldBase):

    def __init__(self, required, nullable):
        self.instance = datetime.datetime
        super(DateField, self).__init__(required, nullable)

    def str_to_date(self, value):
        result = False
        if hasattr(value, 'split'):
            value = value.split('.')
            value.reverse()
            try:
                if len(value[0]) < 4:
                    raise ValueError
                result = self.instance(*map(int, value))
            except (TypeError, ValueError):
                return False
        return result

    def validate(self, value):
        date = self.str_to_date(value)
        if date and super(DateField, self).validate(date):
            result = date
        else:
            result = self._error_message(value)
        return result


class BirthDayField(DateField):

    def __init__(self, required, nullable):
        super(BirthDayField, self).__init__(required, nullable)

    def validate(self, value):
        result = super(BirthDayField, self).validate(value)
        if not isinstance(result, AttributeError):
            delta = datetime.datetime.now() - result
            if not 0 < delta.days // 365 < 70:
                return self._error_message(value)
        return result


class GenderField(FieldBase):

    def __init__(self, required, nullable):
        self.instance = int
        super(GenderField, self).__init__(required, nullable)

    def validate(self, value):
        try:
            if value not in {0, 1, 2}:
                raise ValueError
        except (ValueError, TypeError):
            return self._error_message(value)
        return super(GenderField, self).validate(value)


class ClientIDsField(FieldBase):

    def __init__(self, required, nullable=False):
        self.instance = list
        super(ClientIDsField, self).__init__(required, nullable)

    @staticmethod
    def is_valid_id(value):
        return value > 0 if isinstance(value, int) else False

    def validate(self, value):

        result = super(ClientIDsField, self).validate(value)
        if result == True and not isinstance(result, AttributeError):
            if not all(map(self.is_valid_id, value)):
                return self._error_message(value)
        return result


class ClientsInterestsRequest(object):
    __metaclass__ = DeclarativeMeta
    client_ids = ClientIDsField(required=True)
    date = DateField(required=False, nullable=True)


class OnlineScoreRequest(object):
    __metaclass__ = DeclarativeMeta
    first_name = CharField(required=False, nullable=True)
    last_name = CharField(required=False, nullable=True)
    email = EmailField(required=False, nullable=True)
    phone = PhoneField(required=False, nullable=True)
    birthday = BirthDayField(required=False, nullable=True)
    gender = GenderField(required=False, nullable=True)


class MethodRequest(object):
    __metaclass__ = DeclarativeMeta
    account = CharField(required=False, nullable=True)
    login = CharField(required=True, nullable=True)
    token = CharField(required=True, nullable=True)
    arguments = ArgumentsField(required=True, nullable=True)
    method = CharField(required=True, nullable=False)

    @property
    def is_admin(self):
        return self.login == ADMIN_LOGIN


def check_auth(request):
    if request().is_admin:
        digest = hashlib.sha512(datetime.datetime.now().strftime("%Y%m%d%H") + ADMIN_SALT).hexdigest()
    else:
        digest = hashlib.sha512(request.account + request.login + SALT).hexdigest()
    if digest == request.token:
        return True
    return False


def set_attribute(declarative_class, request):
    for attr in dir(declarative_class):
        if not attr.startswith('__') and not hasattr(getattr(declarative_class, attr), 'getter'):
            setattr(declarative_class, attr, request.get(attr, None))
    return declarative_class


def method_handler(request, ctx, store):
    try:
        method_request = set_attribute(MethodRequest, request['body'])
        if not check_auth(method_request):
            logging.error('{} User authentication error'.format(ctx["request_id"]))
            response, code = ERRORS[FORBIDDEN], FORBIDDEN
        else:
            called_method = getattr(MainHTTPHandler, method_request.method)
            if method_request.method == 'online_score':
                ctx['has'] = [
                    attr for attr in dir(method_request) if not (attr.startswith('__') or hasattr(
                        getattr(method_request, attr), 'getter') or getattr(method_request, attr) is None)
                ]
            else:
                ctx['nclients'] = len(method_request.arguments['client_ids'])
            if method_request().is_admin:
                response = '42'
            else:
                response = called_method(store=store, **request['body']['arguments'])
            code = OK
    except AttributeError as err:
        logging.exception('{} {}'.format(ctx["request_id"], err.message))
        response, code = err.message ,INVALID_REQUEST

    return response, code


class MainHTTPHandler(BaseHTTPRequestHandler):
    router = {
        "method": method_handler
    }
    store = Store()

    @staticmethod
    def online_score(**kwargs):
        request = set_attribute(OnlineScoreRequest, kwargs)
        return get_score(kwargs['store'], request.phone, request.email,
                         request.birthday, request.gender,
                         request.first_name, request.last_name)

    @staticmethod
    def clients_interests(**kwargs):
        request = set_attribute(ClientsInterestsRequest, kwargs)
        return get_interests(kwargs['store'], request.client_ids)


    def get_request_id(self, headers):
        return headers.get('HTTP_X_REQUEST_ID', uuid.uuid4().hex)

    def do_POST(self):
        response, code = {}, OK
        context = {"request_id": self.get_request_id(self.headers)}
        request = None
        try:
            data_string = self.rfile.read(int(self.headers['Content-Length']))
            request = json.loads(data_string)
        except:
            code = BAD_REQUEST

        if request:
            path = self.path.strip("/")[-2]
            logging.info("%s: %s %s" % (self.path, data_string, context["request_id"]))
            if path in self.router:
                try:
                    response, code = self.router[path]({"body": request, "headers": self.headers}, context, self.store)
                except Exception, e:
                    logging.exception("Unexpected error: %s" % e)
                    code = INTERNAL_ERROR
            else:
                code = NOT_FOUND

        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        if code not in ERRORS:
            r = {"response": response, "code": code}
        else:
            r = {"error": response or ERRORS.get(code, "Unknown Error"), "code": code}
        context.update(r)
        logging.info(context)
        self.wfile.write(json.dumps(r))
        return


if __name__ == "__main__":
    field = ClientIDsField(required=True)
    field.validate('')
    field = DateField(required=False, nullable=True)
    obj_exc = field.validate(12122017)
    #method_handler({"body": {}, "headers": {}}, {'request_id': 0}, Store())
    field = GenderField(required=False, nullable=True)
    obj_exc = field.validate(0)
    field = ClientIDsField(required=True)
    obj_exc = field.validate([1.0, 2.0, 3.0])
    field = EmailField(required=False, nullable=True)
    obj_exc = field.validate('0')
    attr = PhoneField(required=False, nullable=True)
    res = attr.validate(None)
    request = json.loads(
        u"""
        {"account": "horns&hoofs", "login": "h&f", "method": "online_score",
        "token": "55cc9ce545bcd144300fe9efc28e65d415b923ebb6be1e19d2750a2c03e80dd209a27954dca045e5bb12418e7d89b6d718a9e35af34e14e1d5bcd5a08f21fc95",
        "arguments": {"phone": "79175002040", "email": "stupnikov@otus.ru", "first_name": "Стансилав",
                      "last_name": "Ступников", "birthday": "01.01.1990", "gender": 1}}""".encode('utf8')
    )
    method_handler({
        "body": request,
        "headers": "Content-Type: application/json"}, {'request_id': 123}, Store()
    )

    op = OptionParser()
    op.add_option("-p", "--port", action="store", type=int, default=8080)
    op.add_option("-l", "--log", action="store", default=None)
    (opts, args) = op.parse_args()
    logging.basicConfig(filename=opts.log, level=logging.INFO,
                        format='[%(asctime)s] %(levelname).1s %(message)s', datefmt='%Y.%m.%d %H:%M:%S')
    server = HTTPServer(("localhost", opts.port), MainHTTPHandler)
    logging.info("Starting server at %s" % opts.port)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    server.server_close()
