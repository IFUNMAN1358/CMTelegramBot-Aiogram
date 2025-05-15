import os

from src.infrastructure.configuration.properties.Env import Env

class CMProperties:

    __CM_HOST = None
    __CM_LOCAL_ADDRESS = None
    __CM_LOCAL_PORT = None

    __CM_BOT_X_SERVICE_NAME = None
    __CM_BOT_X_API_KEY = None

    def __init__(self):
        Env.initialize_venv()

        self.__CM_HOST = str(os.environ.get("CM_HOST"))
        self.__CM_LOCAL_ADDRESS = str(os.environ.get("CM_LOCAL_ADDRESS"))
        self.__CM_LOCAL_PORT = int(os.environ.get("CM_LOCAL_PORT"))

        self.__CM_BOT_X_SERVICE_NAME = str(os.environ.get("CM_BOT_X_SERVICE_NAME"))
        self.__CM_BOT_X_API_KEY = str(os.environ.get("CM_BOT_X_API_KEY"))

    def get_cm_host(self):
        return self.__CM_HOST

    def get_cm_local_address(self):
        return self.__CM_LOCAL_ADDRESS

    def get_cm_local_port(self):
        return self.__CM_LOCAL_PORT

    def get_cm_bot_x_service_name(self):
        return self.__CM_BOT_X_SERVICE_NAME

    def get_cm_bot_x_api_key(self):
        return self.__CM_BOT_X_API_KEY

cm_properties = CMProperties()