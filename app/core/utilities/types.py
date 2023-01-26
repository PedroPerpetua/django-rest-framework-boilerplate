from typing import TYPE_CHECKING, Any, TypeVar
from django.db.models import Model
from django.urls.resolvers import URLPattern, URLResolver
from rest_framework.generics import GenericAPIView
from rest_framework.views import APIView


"""
Type alias for common JSON objects. We type alias it as JSON because recursive types are not 100% working, and because
JSON objects are very mutable by themselves (can be dictionaries, lists, etc).
"""
JSON = Any


"""
Alternative JSON definition useful for functions that manipulate JSON: functions that take a JSON object and return
the same object type.
"""
JSON_BASE = dict[str, Any] | list[Any] | Any


"""Type alias for Generic classes that use Models. Identical to _MT_co type in `rest_framework-stubs.generics`."""
GenericModel = TypeVar("GenericModel", bound=Model, covariant=True)


"""Type alias specifically for urlpatterns lists."""
URLPatternsList = list[URLPattern | URLResolver]

"""Type alias for Mixins."""
if TYPE_CHECKING:
    GenericViewMixin = GenericAPIView
    APIViewMixin = APIView
else:
    GenericViewMixin = object
    APIViewMixin = object
