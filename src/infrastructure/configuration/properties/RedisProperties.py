import os

from src.infrastructure.configuration.properties.Env import Env

class RedisProperties:

    __REDIS_HOST = None
    __REDIS_PORT = None
    __REDIS_USERNAME = None
    __REDIS_PASSWORD = None
    __REDIS_DB_0 = None

    def __init__(self):
        Env.initialize_venv()

        self.__REDIS_HOST = str(os.environ.get("REDIS_HOST"))
        self.__REDIS_PORT = int(os.environ.get("REDIS_PORT"))
        self.__REDIS_USERNAME = str(os.environ.get("REDIS_USERNAME"))
        self.__REDIS_PASSWORD = str(os.environ.get("REDIS_PASSWORD"))
        self.__REDIS_DB_0 = int(os.environ.get("REDIS_DB_0"))

    def get_redis_host(self):
        return self.__REDIS_HOST

    def get_redis_port(self):
        return self.__REDIS_PORT

    def get_redis_username(self):
        return self.__REDIS_USERNAME

    def get_redis_password(self):
        return self.__REDIS_PASSWORD

    def get_redis_db_0(self):
        return self.__REDIS_DB_0