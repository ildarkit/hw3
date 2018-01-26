#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import time
import redis


def exept_handler(method):
    def wrapper(self, *args, **kwargs):
        response = None
        try:
            response = method(self, *args, **kwargs)
        except:
            pass
        return response
    return wrapper


class Store:
    """Класс предоставляет интерфейс к хранилищу redis

    Метод connect без параметров вызовет ping из redis.client,
    который в модуле redis.connection создаст сокет
    или использует уже созданный и выполнит connect.

    В метод connect класса можно передать комманду с аргументами, например redis.get с ключем.
    В таком случае вернется результат выполнения комманды из redis.
    В методе get это сделано для того, чтобы иметь возможность attempts попыток подключения
    прежде чем бросить исключение.

    """
    def __init__(self, host='localhost', port=6379, timeout=3, connect_timeout=20, connect_delay=1, attempts=0):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.connect_timeout = connect_timeout
        self.connect_delay = connect_delay
        self.attempts = attempts
        self.i = 0
        self.redis = redis.Redis(host=self.host, port=self.port, db=0,
                                 socket_timeout=self.timeout,
                                 socket_connect_timeout=self.connect_timeout)

    def connect(self, command=None, *args):
        result = ''
        self.i = 0
        while True:
            try:
                if command is None:
                    self.redis.ping()
                else:
                    result = command(*args)
                break
            except (redis.ConnectionError, redis.TimeoutError):
                time.sleep(self.connect_delay)
                if self.attempts and self.i == self.attempts:
                    raise
                else:
                    self.i += 1
        if result:
            return result

    @exept_handler
    def cache_get(self, key):
        response = self.redis.get(key)
        if response is not None:
            try:
                response = json.loads(response)
            except ValueError:
                pass
        return response

    @exept_handler
    def cache_set(self, key, value, expire):
        return self.redis.set(key, value, ex=expire)

    def get(self, key):
        response = self.connect(self.redis.lrange, key, 0, -1)
        return response


