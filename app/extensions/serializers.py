from typing import Any, Literal
from rest_framework.relations import PKOnlyObject
from rest_framework.serializers import ModelSerializer, PrimaryKeyRelatedField
from drf_spectacular.extensions import OpenApiSerializerFieldExtension
from drf_spectacular.openapi import AutoSchema


class NestedPrimaryKeyRelatedField(PrimaryKeyRelatedField):
    """
    Custom field to serializer a related Foreign Key in a way that it's used as a PK, but on representation it's
    serialized according to the given serializer.

    Based on this issue: https://github.com/tfranzel/drf-spectacular/issues/778
    """

    def __init__(self, serializer: type[ModelSerializer], **kwargs: Any) -> None:
        """
        On read display a complete nested representation of the object(s).
        On write only require the PK (not an entire object) as value.
        """
        self.serializer = serializer
        kwargs.setdefault("queryset", serializer.Meta.model._default_manager.all())  # type: ignore[attr-defined]
        super().__init__(**kwargs)

    def to_representation(self, obj: PKOnlyObject) -> Any:
        model_obj = self.get_queryset().get(pk=obj.pk)
        return self.serializer(model_obj, context=self.context).to_representation(model_obj)


class NestedPrimaryKeyRelatedFieldSerializerExtension(OpenApiSerializerFieldExtension):  # pragma: no cover
    """
    DRF Spectacular extension to deal with the NestedPrimaryKeyRelatedField defined above.

    Extensions register automatically, so if the field above is imported, this extension will be registered.

    **Note**: `COMPONENT_SPLIT_REQUEST` must be `True` in the DRF Spectacular settings for this to work.
    """

    target_class = NestedPrimaryKeyRelatedField
    target: NestedPrimaryKeyRelatedField

    def map_serializer_field(
        self, auto_schema: AutoSchema, direction: Literal["request", "response"]
    ) -> dict[str, Any]:
        """
        Override the serialization so that, in the response, we use the field's serializer; and in the request, we use
        the default value instead.
        """
        if direction == "response":
            component = auto_schema.resolve_serializer(self.target.serializer, direction)
            return component.ref
        # Return the default value for the request (regular serialization)
        default: dict[str, Any] = auto_schema._map_serializer_field(self.target, direction, bypass_extensions=True)
        return default
