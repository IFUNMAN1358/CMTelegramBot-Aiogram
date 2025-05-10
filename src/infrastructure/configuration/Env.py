import os

from dotenv import load_dotenv

class Env:

    __BOT_TOKEN = None
    __WEBHOOK_HOST = None
    __WEBHOOK_PATH = None
    __WEBHOOK_URL = None
    __LOCAL_ADDRESS = None
    __LOCAL_PORT = None

    def __init__(self):
        self.__initialize_venv()

        self.__BOT_TOKEN = str(os.environ.get("BOT_TOKEN"))
        self.__WEBHOOK_HOST = str(os.environ.get("WEBHOOK_HOST"))
        self.__WEBHOOK_PATH = str(os.environ.get("WEBHOOK_PATH"))
        self.__WEBHOOK_URL = f"{self.__WEBHOOK_HOST}{self.__WEBHOOK_PATH}"
        self.__LOCAL_ADDRESS = str(os.environ.get("LOCAL_ADDRESS"))
        self.__LOCAL_PORT = int(os.environ.get("LOCAL_PORT"))


    @staticmethod
    def __initialize_venv():
        load_dotenv()

    @property
    def BOT_TOKEN(self):
        return self.__BOT_TOKEN

    @property
    def WEBHOOK_HOST(self):
        return self.__WEBHOOK_HOST

    @property
    def WEBHOOK_PATH(self):
        return self.__WEBHOOK_PATH

    @property
    def WEBHOOK_URL(self):
        return self.__WEBHOOK_URL

    @property
    def LOCAL_ADDRESS(self):
        return self.__LOCAL_ADDRESS

    @property
    def LOCAL_PORT(self):
        return self.__LOCAL_PORT