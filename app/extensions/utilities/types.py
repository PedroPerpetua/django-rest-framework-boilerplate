from typing import TYPE_CHECKING, Generic, TypeAlias, TypeVar
from django.contrib.auth.models import AbstractBaseUser
from django.db.models import Model
from django.urls.resolvers import URLPattern, URLResolver
from rest_framework.generics import GenericAPIView
from rest_framework.views import APIView


JSON: TypeAlias = dict[str, "JSON"] | list["JSON"] | str | int | float | bool | None
"""Type alias for JSON objects"""


GenericModel = TypeVar("GenericModel", bound=Model, covariant=True)
"""Type alias for Generic classes that use Models. Identical to _MT_co type in `rest_framework-stubs.generics`."""


GenericUser = TypeVar("GenericUser", bound=AbstractBaseUser)
"""Type alias for Generic classes that use some kind of User."""

URLPatternsList: TypeAlias = list[URLPattern | URLResolver]
"""Type alias specifically for urlpatterns lists."""


"""Type alias for Mixins."""
if TYPE_CHECKING:
    GenericViewMixin: TypeAlias = GenericAPIView
    APIViewMixin: TypeAlias = APIView
else:
    GenericViewMixin = object
    APIViewMixin = object


"""Type alias for the generic UsesQueryset."""
if TYPE_CHECKING:
    from rest_framework.generics import UsesQuerySet as BaseUsesQuerySet

    UsesQuerySet: TypeAlias = BaseUsesQuerySet
else:
    UsesQuerySet = Generic
