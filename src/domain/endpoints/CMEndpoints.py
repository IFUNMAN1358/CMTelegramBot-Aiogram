from src.infrastructure.configuration.properties.CMProperties import CMProperties

class CMEndpoints:

    def __init__(self):
        self.__cm_properties = CMProperties()

    #
    # ExternalAuthController
    #

    def POST_api_external_v1_auth_login(self):
        return f"{self.__cm_properties.get_cm_host()}/api/external/v1/auth/login"

    #
    # ExternalServiceController
    #

    def POST_api_external_service(self):
        return f"{self.__cm_properties.get_cm_host()}/api/external-service"

    def GET_api_external_service(self, service_name: str):
        return f"{self.__cm_properties.get_cm_host()}/api/external-service/{service_name}"

    def GET_api_external_services(self):
        return f"{self.__cm_properties.get_cm_host()}/api/external-services"

    def PATCH_api_external_service(self, service_name: str):
        return f"{self.__cm_properties.get_cm_host()}/api/external-service/{service_name}"

    def DELETE_api_external_service(self, service_name: str):
        return f"{self.__cm_properties.get_cm_host()}/api/external-service/{service_name}"

    #
    # RegistrationKeyController
    #

    def POST_api_registration_key(self):
        return f"{self.__cm_properties.get_cm_host()}/api/registration-key"

    def GET_api_registration_keys(self):
        return f"{self.__cm_properties.get_cm_host()}/api/registration-keys"

    def DELETE_api_registration_key(self, key_id: str):
        return f"{self.__cm_properties.get_cm_host()}/api/registration-key/{key_id}"