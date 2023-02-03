from typing import TYPE_CHECKING, Any, TypeVar
from django.contrib.auth.base_user import AbstractBaseUser
from django.db.models import Model
from django.urls.resolvers import URLPattern, URLResolver
from rest_framework.generics import GenericAPIView
from rest_framework.views import APIView


JSON = Any
"""
Type alias for common JSON objects. We type alias it as JSON because recursive types are not 100% working, and because
JSON objects are very mutable by themselves (can be dictionaries, lists, etc).
"""


JSON_BASE = dict[str, Any] | list[Any] | Any
"""
Alternative JSON definition useful for functions that manipulate JSON: functions that take a JSON object and return
the same object type.
"""

GenericModel = TypeVar("GenericModel", bound=Model, covariant=True)
"""Type alias for Generic classes that use Models. Identical to _MT_co type in `rest_framework-stubs.generics`."""


GenericUser = TypeVar("GenericUser", bound=AbstractBaseUser)
"""Type alias for Generic classes that use some kind of User."""

URLPatternsList = list[URLPattern | URLResolver]
"""Type alias specifically for urlpatterns lists."""


"""Type alias for Mixins."""
if TYPE_CHECKING:
    GenericViewMixin = GenericAPIView
    APIViewMixin = APIView
else:
    GenericViewMixin = object
    APIViewMixin = object
