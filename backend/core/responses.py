from rest_framework.response import Response


def success_response(data=None, message="Success", status=200):
    return Response({
        "message": message,
        "data": data
    }, status=status)


def error_response(message="Something went wrong", errors=None, status=400):
    return Response({
        "message": message,
        "errors": errors
    }, status=status)