from django.db import models
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from extensions.models import AbstractBaseModel
from extensions.serializers import InlineSerializer, NestedPrimaryKeyRelatedField
from extensions.utilities import uuid
from extensions.utilities.test import AbstractModelTestCase


class TestInlineSerializer(AbstractModelTestCase):
    """Test the InlineSerializer."""

    class ConcreteModel(AbstractBaseModel):
        field = models.TextField(default="_field")

        class Meta:
            # Because extensions is not an "installed_app", and related name needs a real installed app name.
            app_label = "core"

    class ChildConcreteModel(AbstractBaseModel):
        parent = models.ForeignKey("ConcreteModel", on_delete=models.DO_NOTHING, related_name="children")
        child_field = models.TextField(default="_child_field")

        class Meta:
            # Because extensions is not an "installed_app", and related name needs a real installed app name.
            app_label = "core"

    MODELS = (ConcreteModel, ChildConcreteModel)

    def setUp(self) -> None:
        self.instance = self.ConcreteModel._default_manager.create()

    def test_as_class(self) -> None:
        """Test generating a serializer class using InlineSerializer."""
        SerializerClass = InlineSerializer(self.ConcreteModel, ("id", "field"))
        self.assertIsInstance(SerializerClass, type(serializers.ModelSerializer))
        serializer_instance = SerializerClass(self.instance)  # type: ignore[operator]
        self.assertEqual({"id": str(self.instance.id), "field": self.instance.field}, serializer_instance.data)

    def test_as_instance(self) -> None:
        """Test generating a serializer instance using InlineSerializer with `as_instance`."""
        serializer_instance = InlineSerializer(self.ConcreteModel, ("id", "field"), as_instance=True)
        self.assertIsInstance(serializer_instance, serializers.ModelSerializer)
        serializer_instance.instance = self.instance
        self.assertEqual({"id": str(self.instance.id), "field": self.instance.field}, serializer_instance.data)

    def test_as_instance_args(self) -> None:
        """Test generating a serializer instance using InlineSerializer by passing serializer arguments to it."""
        serializer_instance = InlineSerializer(self.ConcreteModel, ("id", "field"), self.instance)
        self.assertIsInstance(serializer_instance, serializers.ModelSerializer)
        self.assertEqual({"id": str(self.instance.id), "field": self.instance.field}, serializer_instance.data)

    def test_nested_serializer(self) -> None:
        """Test using the InlineSerializer as a Nested serializer."""
        children_instance = self.ChildConcreteModel._default_manager.create(parent=self.instance)

        class SerializerWithInlineChild(serializers.ModelSerializer[TestInlineSerializer.ConcreteModel]):
            children = InlineSerializer(self.ChildConcreteModel, ("id", "child_field"), many=True)

            class Meta:
                model = self.ConcreteModel
                fields = ("id", "field", "children")

        serializer_instance = SerializerWithInlineChild(self.instance)
        self.assertEqual(
            {
                "id": str(self.instance.id),
                "field": self.instance.field,
                "children": [
                    {
                        "id": str(children_instance.id),
                        "child_field": children_instance.child_field,
                    }
                ],
            },
            serializer_instance.data,
        )

    def test_name_property(self) -> None:
        """Test the name applied to `__name__`."""
        with self.subTest("Test default name"):
            SerializerClass = InlineSerializer(self.ConcreteModel, ("id", "field"))
            self.assertEqual(
                SerializerClass.__name__,  # type: ignore[attr-defined]
                f"{self.ConcreteModel.__name__}InlineSerializer",
            )
        with self.subTest("Test custom name"):
            custom_name = uuid()
            SerializerClass = InlineSerializer(self.ConcreteModel, ("id", "field"), serializer_name=custom_name)
            self.assertEqual(
                SerializerClass.__name__,  # type: ignore[attr-defined]
                custom_name,
            )


class TestNestedPrimaryKeyRelatedField(AbstractModelTestCase):
    """Test the NestedPrimaryKeyRelatedField."""

    class ConcreteChildModel(AbstractBaseModel):
        field1 = models.TextField(default="_field1")
        field2 = models.TextField(default="_field2")

        class Meta:
            # Because extensions is not an "installed_app", and related name needs a real installed app name.
            app_label = "core"

    class ConcreteParentModel(AbstractBaseModel):
        child = models.OneToOneField("ConcreteChildModel", on_delete=models.DO_NOTHING, related_name="reverse")

        class Meta:
            # Because extensions is not an "installed_app", and related name needs a real installed app name.
            app_label = "core"

    MODELS = (ConcreteChildModel, ConcreteParentModel)

    def setUp(self) -> None:
        class ChildeSerializer(serializers.ModelSerializer):
            class Meta:
                model = self.ConcreteChildModel
                fields = ("field1", "field2")

        self.childSerializer = ChildeSerializer

        class ParentSerializer(serializers.ModelSerializer):
            child = NestedPrimaryKeyRelatedField(ChildeSerializer)

            class Meta:
                model = self.ConcreteParentModel
                fields = ("child",)

        self.parentSerializer = ParentSerializer

        return super().setUp()

    def test_creation(self) -> None:
        """Test using the serializer to create a parent instance."""
        child = self.ConcreteChildModel._base_manager.create()
        original_count = self.ConcreteParentModel._base_manager.count()
        serialized_parent = self.parentSerializer(data={"child": child.pk})
        serialized_parent.is_valid(raise_exception=True)
        parent = serialized_parent.save()
        # Check that it was created correctly
        self.assertEqual(original_count + 1, self.ConcreteParentModel._base_manager.count())
        self.assertEqual(parent.child, child)

    def test_creation_nested_data_fails(self) -> None:
        """Test using the serializer to create a parent instance with nested data instead of id fails."""
        serialized_child_data = {"field1": "_field1", "field2": "_field2"}
        serialized_parent = self.parentSerializer(data={"child": serialized_child_data})
        with self.assertRaises(ValidationError) as ctx:
            serialized_parent.is_valid(raise_exception=True)
        self.assertEqual(ctx.exception.get_codes(), {"child": ["invalid"]})

    def test_representation(self) -> None:
        """Test that retrieving the presentation will display the nested data."""
        child = self.ConcreteChildModel._base_manager.create()
        parent = self.ConcreteParentModel._base_manager.create(child=child)
        serialized_parent = self.parentSerializer(parent)
        data = serialized_parent.data
        self.assertEqual(self.childSerializer(child).data, data["child"])
