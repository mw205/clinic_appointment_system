from django.http import Http404
from django.core.exceptions import ValidationError as DjangoValidationError

from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework.exceptions import (
    ValidationError,
    PermissionDenied,
    NotAuthenticated,
    AuthenticationFailed,
    NotFound,
    MethodNotAllowed,
    Throttled,
    APIException,
)


def map_exception(exc):
    if isinstance(exc, (ValidationError, DjangoValidationError)):
        return "validation_error", "Invalid input."

    if isinstance(exc, NotAuthenticated):
        return "not_authenticated", "Authentication required."

    if isinstance(exc, AuthenticationFailed):
        return "authentication_failed", "Invalid credentials."

    if isinstance(exc, PermissionDenied):
        return "permission_denied", "Permission denied."

    if isinstance(exc, (NotFound, Http404)):
        return "not_found", "Resource not found."

    if isinstance(exc, MethodNotAllowed):
        return "method_not_allowed", "Method not allowed."

    if isinstance(exc, Throttled):
        return "throttled", "Too many requests."

    if isinstance(exc, APIException):
        return getattr(exc, "default_code", "api_error"), str(exc.detail)

    return "server_error", "Something went wrong."

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    code, message = map_exception(exc)

    if response is None:
        return Response(
            {
                "code": "server_error",
                "message": "Internal server error."
            },
            status=500,
        )

    details = None
    if isinstance(exc, (ValidationError, DjangoValidationError)):
        details = response.data

    data = {
        "code": code,
        "message": message,
    }

    if details:
        data["details"] = details

    return Response(data, status=response.status_code)