#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import time
import logging

import redis


def exept_handler(method):
    def wrapper(self, *args):
        response = None
        try:
            response = method(self, *args)
        except (redis.ConnectionError, redis.TimeoutError) as err:
            logging.info('<{}> method with args {} not executed ({})'.format(method.__name__, args, err.message))
        except ValueError as err:
            logging.error('The response can not be represented as a number:\n{}'.format(err.message))
        return response
    return wrapper


class Store(object):
    """Класс предоставляет интерфейс к хранилищу redis"""
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

    def connect(self):
        self.i = 0
        while True:
            try:
                connection = self.redis.connection_pool.get_connection('')
                connection.connect()
                self.redis.connection_pool.release(connection)
                break
            except (redis.ConnectionError, redis.TimeoutError):
                time.sleep(self.connect_delay)
                if self.attempts and self.i == self.attempts:
                    raise
                else:
                    self.i += 1

    @staticmethod
    def reconnect(method):
        def wrapper(self, *args):
            try:
                return method(self, *args)
            except (redis.ConnectionError, redis.TimeoutError):
                self.connect()
                return method(self, *args)
        return wrapper

    @exept_handler
    @reconnect.__func__
    def cache_get(self, key):
        response = self.redis.get(key)
        if response is not None:
            response = json.loads(response)
        return response

    @exept_handler
    @reconnect.__func__
    def cache_set(self, key, value, expire):
        return self.redis.set(key, value, ex=expire)

    @reconnect.__func__
    def get(self, key):
        response = self.redis.lrange(key, 0, -1)
        return response
