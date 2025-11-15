from typing import Any, Iterable, Literal, Optional, Protocol, overload
from django.db.models import Model, QuerySet
from rest_framework.relations import PKOnlyObject
from rest_framework.serializers import ModelSerializer, PrimaryKeyRelatedField
from drf_spectacular.extensions import OpenApiSerializerFieldExtension
from drf_spectacular.openapi import AutoSchema


class InlineSerializer[_MT: Model](ModelSerializer[_MT]):
    """
    An inline serializer class that allows the creation of very simple serializers for one-of uses and such without
    having to define an entire serializer class.

    Example usage:
    ```
    # The serializer class defined by...
    MySerializer = InlineSerializer(MyModel, ("id", "field1", "field2")
    # Is equivalent to...
    class MySerializer(ModelSerializer[MyModel]):

        class Meta:
            model = MyModel
            fields = ("id", "field1", "field2")

    # The instance defined by...
    instance = InlineSerializer(MyModel, ("id", "field1", "field2"), many=True)
    # Is equivalent to...
    class MySerializer(ModelSerializer[MyModel]):

        class Meta:
            model = MyModel
            fields = ("id", "field1", "field2")
    instance = MySerializer(many=True)

    # Using it in a view
    class MyView(generics.ListView[MyModel]):
        serializer_class = InlineSerializer(MyModel, ("id",))

    # Using it as a nested field in a Serializer
    class MySerializer(ModelSerializer[MyModel]):
        child = InlineSerializer(ChildModel, ("id", "field1"), as_instance=True)

        class Meta:
            model = MyModel
            fields = ("id", "child")
    ```

    **NOTE**: instantiating an InlineSerializer will, by default, return _the generated serializer **class**_, instead
    of a serializer instance. To get an instance of the generated serializer, pass any regular serializer arguments,
    or, alternatively, `as_instance=True`

    An inline serializer takes the following arguments:
    - `model` - the model type that the generated serializer should be for;
    - `fields` - the fields that should be used in the serializer;
    - `serializer_name` - kwarg optional name for the component name in the generated OpenAPI spec; if none is
    provided, it will default to "<model name>InlineSerializer";
    - `as_instance` - kwarg to indicate that an instance of the serializer should be returned, instead of the
    serializer class itself.
    - All the regular arguments a ModelSerializer takes. If any are passed, an instance of the serializer will be
    returned.

    **NOTE**: There's an issue in Mypy that makes it so that the return type of __new__ doesn't always work properly.
    Mypy will likely read `InlineSerializer(MyModel, ("id",))` as a ModelSerializer _instance_ instead of
    type[ModelSerializer]; it will work as expected, but may need to be type-ignore.
    See: https://github.com/python/mypy/issues/15182
    """

    @overload
    def __new__(  # type: ignore[misc]
        cls,
        ModelClass: type[_MT],
        fields: Iterable[str],
        *,
        serializer_name: Optional[str] = ...,
        as_instance: Literal[False] = ...,
    ) -> type[ModelSerializer[_MT]]: ...

    @overload
    def __new__(  # type: ignore[misc]
        cls,
        ModelClass: type[_MT],
        fields: Iterable[str],
        *args: Any,
        serializer_name: Optional[str] = ...,
        as_instance: Literal[True] = ...,
        **kwargs: Any,
    ) -> ModelSerializer[_MT]: ...

    def __new__(  # type: ignore[misc]
        cls,
        ModelClass: type[_MT],
        fields: Iterable[str],
        *args: Any,
        serializer_name: Optional[str] = None,
        as_instance: bool = False,
        **kwargs: Any,
    ) -> type[ModelSerializer[_MT]] | ModelSerializer[_MT]:
        inner_model = ModelClass
        inner_fields = fields

        class InnerSerializer(ModelSerializer[_MT]):
            class Meta:
                model = inner_model
                fields = inner_fields

        InnerSerializer.__name__ = serializer_name or f"{ModelClass.__name__}InlineSerializer"

        if len(args) or len(kwargs) or as_instance:
            # We want to return an instance
            return InnerSerializer(*args, **kwargs)

        return InnerSerializer


class FilterFunction[_MT: Model](Protocol):
    def __call__(self, context: dict[str, Any], queryset: Optional[QuerySet[_MT]]) -> QuerySet[_MT]: ...


class FilteredPrimaryKeyRelatedField[_MT: Model](PrimaryKeyRelatedField[_MT]):
    """
    PrimaryKeyRelatedField that will be filtered by the `filter_queryset` method that is passed. This method will be
    called with the serializer's context and the field's queryset (if any).

    **NOTE**: because of the way DRF serializers work, the filter function can not be a StaticMethod in the serializer
    class.

    Example usage:
    ```
    def my_filter(context: dict[str, Any], queryset: QuerySet[MyModel]) -> QuerySet[MyModel]:
        # Here, you can use, for example, the `context["request"].user` to filter with the current user
        return queryset.filter(...)

    class MySerializer(ModelSerializer[MyModel]):
        field = FilteredPrimaryRelatedField(filter_queryset=my_filter)
    """

    def __init__(self, *args: Any, filter_queryset: Optional[FilterFunction[_MT]] = None, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._filter_func = filter_queryset

    # https://github.com/typeddjango/djangorestframework-stubs/issues/779
    def get_queryset(self) -> Optional[QuerySet[_MT]]:  # type: ignore[override]
        qs = super().get_queryset()
        if self._filter_func:
            qs = self._filter_func(context=self.context, queryset=qs)
        return qs


class NestedPrimaryKeyRelatedField[_MT: Model](FilteredPrimaryKeyRelatedField[_MT]):
    """
    Custom field to serializer a related Foreign Key in a way that it's used as a PK, but on representation it's
    serialized according to the given serializer.

    Based on this issue: https://github.com/tfranzel/drf-spectacular/issues/778
    """

    def __init__(self, serializer: type[ModelSerializer[_MT]], **kwargs: Any) -> None:
        """
        On read display a complete nested representation of the object(s).
        On write only require the PK (not an entire object) as value.
        """
        self._serializer = serializer
        kwargs.setdefault("queryset", serializer.Meta.model._default_manager.all())  # type: ignore[attr-defined]
        super().__init__(**kwargs)

    def to_representation(self, obj: _MT | PKOnlyObject) -> Any:
        qs = self.get_queryset()
        # Because we set the default queryset in the `__init__` we should always have a QuerySet here
        assert isinstance(qs, QuerySet)
        model_obj = qs.get(pk=obj.pk)
        return self._serializer(model_obj, context=self.context).to_representation(model_obj)


class NestedPrimaryKeyRelatedFieldSerializerExtension(OpenApiSerializerFieldExtension):  # pragma: no cover
    """
    DRF Spectacular extension to deal with the NestedPrimaryKeyRelatedField defined above.

    Extensions register automatically, so if the field above is imported, this extension will be registered.

    **Note**: `COMPONENT_SPLIT_REQUEST` must be `True` in the DRF Spectacular settings for this to work.
    """

    target_class = NestedPrimaryKeyRelatedField
    target: NestedPrimaryKeyRelatedField

    def map_serializer_field(
        self,
        auto_schema: AutoSchema,
        direction: Literal["request", "response"],
    ) -> dict[str, Any]:
        """
        Override the serialization so that, in the response, we use the field's serializer; and in the request, we use
        the default value instead.
        """
        if direction == "response":
            component = auto_schema.resolve_serializer(self.target._serializer, direction)
            return component.ref
        # Return the default value for the request (regular serialization)
        default: dict[str, Any] = auto_schema._map_serializer_field(self.target, direction, bypass_extensions=True)
        return default
