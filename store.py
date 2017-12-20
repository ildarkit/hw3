import json
import redis


class Store:
    def __init__(self, host='localhost', port=6379, timeout=3, connect_timeout=20, attempts=3):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.connect_timeout = connect_timeout
        self.attempts = attempts
        self.i = 0
        self._try_connect()

    def _try_connect(self):
        try:
            self.redis = redis.Redis(host=self.host, port=self.port,
                                     socket_timeout=self.timeout, socket_connect_timeout=self.connect_timeout
                                     )
        except (redis.ConnectionError, redis.TimeoutError):
            self.i += 1
            if self.i <= self.attempts:
                self._try_connect()
            else:
                raise

    @staticmethod
    def _exec_command(command, *args, **kwargs):
        response = None
        try:
            response = command(*args, **kwargs)
        except (redis.ConnectionError, redis.TimeoutError):
            pass
        return response

    def cache_get(self, key):
        return self._exec_command(self.get, key)

    def cache_set(self, key, value, expire):
        return self._exec_command(self.redis.set, key, value, ex=expire)

    def get(self, key):
        response = self.redis.get(key)
        if not response is None:
            response = json.loads(response)
        return response
