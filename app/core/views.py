from typing import Any
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response


class PingView(APIView):
    """View that simply replies with a 'pong'."""
    http_method_names = ["get"]

    def get(self, *args: Any, **kwargs: Any) -> Response:
        return Response("pong", status=status.HTTP_200_OK)
