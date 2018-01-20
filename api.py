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
try:
    STR_TYPE = basestring
    PYTHON2 = True
except NameError:
    STR_TYPE = str
    PYTHON2 = False
NOT_EMPTY_GROUP_ATTR = (('phone', 'email'), ('first_name', 'last_name'), ('birthday', 'gender'))
VALIDATION_ERROR_MESSAGE = False


class BaseAttributeError(Exception):
    """
    Базовый класс ошибок, возникающих при валидации атрибута (поля).
    На проверке на истинность возвращает False.
    """
    def __nonzero__(self):
        return False

    def __bool__(self):
        self.__nonzero__()

    def format(self, *args):
        return self.message.format(*args)


class RequiredAttributeError(BaseAttributeError):
    """
    Возникает при не соблюдении обязательности атрибута,
    т.е. если значение None
    """
    def __init__(self, *args, **kwargs):
        self.message = '{}: attribute <{}> is required'
        super(RequiredAttributeError, self).__init__(*args, **kwargs)


class NotNullableAttributeError(BaseAttributeError):
    """
    Возникает при не соблюдении правила на "пустость" атрибута
    """
    def __init__(self, *args, **kwargs):
        self.message = '{}: attribute <{}> is not nullable'
        super(NotNullableAttributeError, self).__init__(*args, **kwargs)


class TypeAttributeError(BaseAttributeError):
    """
    Возникает при не соответствии значения типу атрибута
    """
    def __init__(self, *args, **kwargs):
        self.message = '{}: invalid type {} of value <{}> for attribute <{}>'
        super(TypeAttributeError, self).__init__(*args, **kwargs)


class InvalidAttributeError(BaseAttributeError):
    """
    Возникает при не верных значениях
    """
    def __init__(self, *args, **kwargs):
        self.message = '{}: invalid value <{}> for attribute <{}>'
        super(InvalidAttributeError, self).__init__(*args, **kwargs)


class DeclarativeMeta(type):

    def __setattr__(cls, attr, value):
        try:
            attribute = cls.__dict__[attr]
        except KeyError:
            pass
        else:
            if hasattr(attribute, 'validate'):
                result = attribute.validate(value)
                if result:
                    cls.__dict__[attr].value = value
                else:
                    result.message = result.format(cls.__name__, attr)
                    raise result


class FieldBase(object):
    def __init__(self, required, nullable):
        self.required = required
        self.nullable = nullable

    def validate(self, value):
        # return True or Error
        result = True
        if value is None:
            if self.required:
                result = RequiredAttributeError()
        elif value != '' and not isinstance(value, self.instanceof):
            result = TypeAttributeError()
            result.message = result.format('{}', type(value), value, '{}')
        elif not (value or self.nullable):
            result = NotNullableAttributeError()
        return result

    def __get__(self, instance, owner):
        if hasattr(self, 'value'):
            return self.value

    @staticmethod
    def _invalid_value(value):
        err = InvalidAttributeError()
        err.message = err.format('{}', value, '{}')
        return err


class CharField(FieldBase):
    def __init__(self, required, nullable):
        self.instanceof = STR_TYPE
        super(CharField, self).__init__(required, nullable)


class ArgumentsField(FieldBase):
    def __init__(self, required, nullable):
        self.instanceof = dict
        super(ArgumentsField, self).__init__(required, nullable)


class EmailField(CharField):
    def __init__(self, required, nullable):
        super(EmailField, self).__init__(required, nullable)

    def validate(self, value):
        result = super(CharField, self).validate(value)
        if result is True:
            result = result if '@' in value else self._invalid_value(value)
        return result


class PhoneField(FieldBase):
    def __init__(self, required, nullable):
        self.instanceof = STR_TYPE
        super(PhoneField, self).__init__(required, nullable)

    def validate(self, value):
        try:
            if value:
                int(value)
        except ValueError:
            return self._invalid_value(value)
        else:
            result = super(PhoneField, self).validate(value)
            if result is True and not (len(value) == 11 and value[0] == '7'):
                result = self._invalid_value(value)
            return result


class DateField(FieldBase):
    def __init__(self, required, nullable):
        self.instanceof = STR_TYPE
        super(DateField, self).__init__(required, nullable)

    @staticmethod
    def str_to_date(value):
        result = value
        if value and hasattr(value, 'split'):
            value = value.split('.')
            value.reverse()
            try:
                if len(value[0]) == 4:
                    result = datetime.datetime(*map(int, value))
                else:
                    result = False
            except (TypeError, ValueError):
                result = False
        return result

    def validate(self, value):
        result = super(DateField, self).validate(value)
        if result:
            date = self.str_to_date(value)
            if date is False:
                result = self._invalid_value(value)
            else:
                result = date
        return result


class BirthDayField(DateField):
    def __init__(self, required, nullable):
        super(BirthDayField, self).__init__(required, nullable)

    def validate(self, value):
        result = super(BirthDayField, self).validate(value)
        if result:
            delta = datetime.datetime.now() - result
            if not 0 < delta.days // 365 < 70:
                return self._invalid_value(value)
        return result


class GenderField(FieldBase):
    def __init__(self, required, nullable):
        self.instanceof = int
        super(GenderField, self).__init__(required, nullable)

    def validate(self, value):
        result = super(GenderField, self).validate(value)
        if result:
            if value not in {0, 1, 2}:
                result = self._invalid_value(value)
            else:
                result = value
        return result


class ClientIDsField(FieldBase):
    def __init__(self, required, nullable=False):
        self.instanceof = list
        super(ClientIDsField, self).__init__(required, nullable)

    @staticmethod
    def is_valid_id(value):
        return value > 0 if isinstance(value, int) else False

    def validate(self, value):
        result = super(ClientIDsField, self).validate(value)
        if result and not all(map(self.is_valid_id, value)):
            return self._invalid_value(value)
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


def set_attributes(declarative_class, request):
    for attr in dir(declarative_class):
        if not attr.startswith('__') and not hasattr(getattr(declarative_class, attr), 'getter'):
            # setattr вызовет __setattr__ в метаклассе DeclarativeMeta
            setattr(declarative_class, attr, request.get(attr, None))
    return declarative_class


def is_empty_value_in_group_attr(arguments):
    result = True
    for group_attr in NOT_EMPTY_GROUP_ATTR:
        if len([attr for attr in group_attr if arguments.get(attr, '')]) == len(group_attr):
            result = False
            break
    return result


def method_handler(request, ctx):
    response = ''
    try:
        method_request = set_attributes(MethodRequest, request['body'])
        if not check_auth(method_request):
            logging.error('{} User authentication error'.format(ctx["request_id"]))
            response, code = ERRORS[FORBIDDEN], FORBIDDEN
        else:
            requested_method = getattr(MainHTTPHandler, method_request.method)
            if method_request.method == 'online_score':
                # в словаре контекста создаем список не пустых полей
                ctx['has'] = [
                    attr for attr in dir(method_request) if not (attr.startswith('__') or hasattr(
                        getattr(method_request, attr), 'getter') or getattr(method_request, attr) is None)
                ]
                # хотя бы одна пара полей из NOT_EMPTY_GROUP_ATTR должна быть с не пустыми значениями
                if is_empty_value_in_group_attr(method_request.arguments):
                    raise AttributeError(
                        '{}: there are empty values ​​in all attribute groups {}'.format(
                            method_request.__class__.__name__,
                            ', '.join(map(repr, NOT_EMPTY_GROUP_ATTR))
                        )
                    )
                if method_request().is_admin:
                    response = {'score': 42}
            # method: clients_interests
            else:
                # вычисление кол-ва переданных id клиентов
                # и сохранение в словаре контекста
                clients_ids = set(method_request.arguments['client_ids'])
                ctx['nclients'] = len(clients_ids)
            if not response:
                # вызов запрашиваемого метода из MainHTTPHandler
                response = json.dumps(requested_method(MainHTTPHandler, **request['body']['arguments']))
            code = OK
    except (RequiredAttributeError, NotNullableAttributeError, TypeAttributeError,
            InvalidAttributeError, AttributeError) as err:
        if VALIDATION_ERROR_MESSAGE:
            logging.error('{} {}'.format(ctx["request_id"], err.message))
        response, code = err.message, INVALID_REQUEST
    return response, code


class MainHTTPHandler(BaseHTTPRequestHandler):
    router = {
        "method": method_handler
    }
    # connect без параметров вызовет ping из redis.client,
    # который в модуле redis.connection создаст сокет
    # или использует уже созданный и выполнит connect
    store = Store()
    store.connect()

    @staticmethod
    def online_score(cls, **kwargs):
        request = set_attributes(OnlineScoreRequest, kwargs)
        birthday = DateField.str_to_date(request.birthday)
        result = dict()
        if PYTHON2:
            first_name = request.first_name.encode('utf-8')
            last_name = request.last_name.encode('utf-8')
        else:
            first_name = request.first_name
            last_name = request.last_name

        result['score'] = get_score(cls.store, request.phone, request.email,
                                    birthday, request.gender,
                                    first_name, last_name)
        return result

    @staticmethod
    def clients_interests(cls, **kwargs):
        request = set_attributes(ClientsInterestsRequest, kwargs)
        result = dict()
        for cid in request.client_ids:
            result[cid] = get_interests(cls.store, cid)
        return result

    def get_request_id(self, headers):
        return headers.get('HTTP_X_REQUEST_ID', uuid.uuid4().hex)

    def do_POST(self):
        response, code = {}, OK
        context = {"request_id": self.get_request_id(self.headers)}
        request = None
        try:
            data_string = self.rfile.read(int(self.headers['Content-Length']))
            request = json.loads(data_string, encoding='utf-8')
        except Exception:
            code = BAD_REQUEST

        if request:
            logging.info(self.path)
            path = self.path.strip("/")
            logging.info("%s: %s %s" % (self.path, data_string, context["request_id"]))
            if path in self.router:
                try:
                    response, code = self.router[path]({"body": request, "headers": self.headers}, context)
                except Exception as e:
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
    VALIDATION_ERROR_MESSAGE = True
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
