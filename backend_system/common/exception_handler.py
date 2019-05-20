from django.http import Http404

from rest_framework import status
from rest_framework.exceptions import APIException, ValidationError
from rest_framework.response import Response


def exception_handler(exc, context):

    if isinstance(exc, ValidationError):
        data = {
            'error': 'ValidationError',
            'error_description': exc.detail or 'Invalid input.'
        }

        return Response(data, status=exc.status_code)

    elif isinstance(exc, APIException):
        data = {
            'error': exc.__class__.__name__,
            'error_description': exc.detail
        }

        return Response(data, status=exc.status_code)

    elif isinstance(exc, Http404):
        data = {
            'error': 'NotFound',
            'error_description': 'Item Not found.'
        }
        return Response(data, status=status.HTTP_404_NOT_FOUND)

    else:
        data = {
            'error': 'InternalServerError',
            'error_description': 'An unknown error occurred.'
        }

        return Response(data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
