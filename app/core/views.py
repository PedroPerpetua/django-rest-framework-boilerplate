from typing import Any
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema


@extend_schema(tags=["Core"])
class PingView(APIView):
    """View that simply replies with a 'pong'."""

    http_method_names = ["get"]

    @extend_schema(operation_id="healthcheck")
    @extend_schema(summary="Healthcheck")
    @extend_schema(responses={status.HTTP_200_OK: {"type": "string", "enum": ["pong"]}})
    def get(self, *args: Any, **kwargs: Any) -> Response:
        return Response("pong", status=status.HTTP_200_OK)
