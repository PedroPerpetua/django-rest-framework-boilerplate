from typing import Any
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from constance import config  # type: ignore[import-untyped]
from drf_spectacular.utils import extend_schema
from drf_spectacular.views import SpectacularAPIView as BaseSpectacularAPIView
from drf_spectacular.views import SpectacularSwaggerView as BaseSpectacularSwaggerView


@extend_schema(tags=["Core"])
class PingView(APIView):
    """View that simply replies with a 'pong'."""

    permission_classes = (AllowAny,)
    http_method_names = ("get",)

    @extend_schema(operation_id="ping")
    @extend_schema(summary="Ping")
    @extend_schema(responses={status.HTTP_200_OK: {"type": "string", "enum": ["pong"]}})
    def get(self, *args: Any, **kwargs: Any) -> Response:
        return Response("pong", status=status.HTTP_200_OK)


class SpectacularAPIView(BaseSpectacularAPIView):
    """Custom SpectacularAPIView so that we can configure the permissions from the Constance config."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.permission_classes = (IsAdminUser,) if config.OPENAPI_ADMIN_ONLY else (AllowAny,)


class SpectacularSwaggerView(BaseSpectacularSwaggerView):
    """Custom SpectacularSwaggerView so that we can configure the permissions from the Constance config."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.permission_classes = (IsAdminUser,) if config.OPENAPI_ADMIN_ONLY else (AllowAny,)
