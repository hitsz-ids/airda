import redis
from dg_agent.config import System
from dg_agent.db import DB
from overrides import override


class Redis:
    def __init__(self, db_uri, db_port, db_pwd):
        db_uri = db_uri
        db_port = db_port
        db_pwd = db_pwd
        self.client = redis.StrictRedis(host=db_uri, port=db_port, password=db_pwd, db=0)

    def set(self, key, value):
        self.client.set(key, value)

    def get(self, key):
        return self.client.get(key)

    def delete(self, key):
        self.client.delete(key)

    def update(self, key, value):
        if self.client.exists(key):
            self.set(key, value)
        else:
            raise KeyError(f"Key '{key}' does not exist.")
