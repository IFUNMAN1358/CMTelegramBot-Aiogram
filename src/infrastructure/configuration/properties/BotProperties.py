import os

from src.infrastructure.configuration.properties.Env import Env

class BotProperties:

    __BOT_TOKEN = None
    __BOT_WEBHOOK_HOST = None
    __BOT_WEBHOOK_PATH = None
    __BOT_WEBHOOK_URL = None
    __BOT_LOCAL_ADDRESS = None
    __BOT_LOCAL_PORT = None

    def __init__(self):
        Env.initialize_venv()

        self.__BOT_TOKEN = str(os.environ.get("BOT_TOKEN"))
        self.__BOT_WEBHOOK_HOST = str(os.environ.get("BOT_WEBHOOK_HOST"))
        self.__BOT_WEBHOOK_PATH = str(os.environ.get("BOT_WEBHOOK_PATH"))
        self.__BOT_WEBHOOK_URL = f"{self.__BOT_WEBHOOK_HOST}{self.__BOT_WEBHOOK_PATH}"
        self.__BOT_LOCAL_ADDRESS = str(os.environ.get("BOT_LOCAL_ADDRESS"))
        self.__BOT_LOCAL_PORT = int(os.environ.get("BOT_LOCAL_PORT"))

    def get_bot_token(self):
        return self.__BOT_TOKEN

    def get_bot_webhook_host(self):
        return self.__BOT_WEBHOOK_HOST

    def get_bot_webhook_path(self):
        return self.__BOT_WEBHOOK_PATH

    def get_bot_webhook_url(self):
        return self.__BOT_WEBHOOK_URL

    def get_bot_local_address(self):
        return self.__BOT_LOCAL_ADDRESS

    def get_bot_local_port(self):
        return self.__BOT_LOCAL_PORT