from rest_framework.exceptions import APIException


class ServiceUnavailable(APIException):
    status_code = 500
    default_detail = 'Internal server error, try again later.'
    default_code = 'service_unavailable'