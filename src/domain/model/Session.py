import json


class Session:

    __access_token: str
    __refresh_token: str
    __username: str
    __first_name: str
    __last_name: str | None
    __user_roles: set[str]

    def __init__(self, access_token, refresh_toke, username, first_name, last_name, user_roles):
        self.__access_token = access_token
        self.__refresh_token = refresh_toke
        self.__username = username
        self.__first_name = first_name
        self.__last_name = last_name
        self.__user_roles = user_roles

    @staticmethod
    def from_dict(d: dict):
        return Session(
            d.get("accessToken"),
            d.get("refreshToken"),
            d.get("username"),
            d.get("firstName"),
            d.get("lastName"),
            d.get("userRoles")
        )

    def to_dict(self):
        return {
            "accessToken": self.__access_token,
            "refreshToken": self.__refresh_token,
            "username": self.__username,
            "firstName": self.__first_name,
            "lastName": self.__last_name,
            "userRoles": self.__user_roles
        }

    def get_access_token(self) -> str:
        return self.__access_token

    def get_refresh_token(self) -> str:
        return self.__refresh_token

    def get_username(self) -> str:
        return self.__username

    def get_first_name(self) -> str:
        return self.__first_name

    def get_last_name(self) -> str | None:
        return self.__last_name

    def get_user_roles(self) -> set[str]:
        return self.__user_roles