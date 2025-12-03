from django.db.models import ProtectedError, RestrictedError
from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.response import Response
from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    # Call DRF's default exception handler first to get a default response
    response = exception_handler(exc, context)

    # TODO: Log exc message for dev analysis
    # Handle 500 errors specifically
    if response is None and isinstance(exc, Exception):  # Catch generic Python exceptions
        # Check if the exception is a model deletion constraint
        if isinstance(exc, ProtectedError) or isinstance(exc, RestrictedError):
            # Prepare the response data
            protected_objects = []
            if exc.protected_objects:
                protected_objects = [{"object": str(obj),
                                      "object_name": obj.__class__.__name__} for obj in exc.protected_objects]
            message = {
                "error": "This item can't be deleted. It is used in other records.",
                "code": "protected_error",
                "protected_objects": protected_objects
            }
            # Check if the exception is a model creation constraint
        elif isinstance(exc, CreateException):
            # Error while creating an object
            message = {
                "error": exc.get_full_details(),
                "code": exc.get_codes()
            }
        # Check if the exception is a model update constraint
        elif isinstance(exc, UpdateException):
            # Error while updating an object
            message = {
                "error": exc.get_full_details(),
                "code": exc.get_codes()
            }
        else:
            # Generic error
            message = {
                "error": "Something went wrong, please try again later or contact support.",
                "code": "internal_server_error"
            }

        return Response(
            message,
            status=status.HTTP_400_BAD_REQUEST,
        )

    return response


class CreateException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Error while creating an object.'
    default_code = 'create_error'


class UpdateException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Error while updating the object.'
    default_code = 'update_error'
