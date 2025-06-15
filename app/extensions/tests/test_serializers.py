from typing import Any, Optional
from django.db import models
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from extensions.models import AbstractBaseModel
from extensions.serializers import FilteredPrimaryKeyRelatedField, InlineSerializer, NestedPrimaryKeyRelatedField
from extensions.utilities import uuid
from extensions.utilities.test import AbstractModelTestCase


class TestInlineSerializer(AbstractModelTestCase):
    """
    Test the InlineSerializer.

    Because all ConcreteModels need to be unique within "core", we prefix all of them with "TestA".
    """

    class TestA_ConcreteModel(AbstractBaseModel):
        field = models.TextField(default="_field")

        class Meta:
            # Because extensions is not an "installed_app", and related name needs a real installed app name.
            app_label = "core"

    class TestA_ChildConcreteModel(AbstractBaseModel):
        parent = models.ForeignKey("TestA_ConcreteModel", on_delete=models.DO_NOTHING, related_name="children")
        child_field = models.TextField(default="_child_field")

        class Meta:
            # Because extensions is not an "installed_app", and related name needs a real installed app name.
            app_label = "core"

    MODELS = (TestA_ConcreteModel, TestA_ChildConcreteModel)

    def setUp(self) -> None:
        self.instance = self.TestA_ConcreteModel._default_manager.create()

    def test_as_class(self) -> None:
        """Test generating a serializer class using InlineSerializer."""
        SerializerClass = InlineSerializer(self.TestA_ConcreteModel, ("id", "field"))
        self.assertIsInstance(SerializerClass, type(serializers.ModelSerializer))
        serializer_instance = SerializerClass(self.instance)  # type: ignore[operator]
        self.assertEqual({"id": str(self.instance.id), "field": self.instance.field}, serializer_instance.data)

    def test_as_instance(self) -> None:
        """Test generating a serializer instance using InlineSerializer with `as_instance`."""
        serializer_instance = InlineSerializer(self.TestA_ConcreteModel, ("id", "field"), as_instance=True)
        self.assertIsInstance(serializer_instance, serializers.ModelSerializer)
        serializer_instance.instance = self.instance
        self.assertEqual({"id": str(self.instance.id), "field": self.instance.field}, serializer_instance.data)

    def test_as_instance_args(self) -> None:
        """Test generating a serializer instance using InlineSerializer by passing serializer arguments to it."""
        serializer_instance = InlineSerializer(self.TestA_ConcreteModel, ("id", "field"), self.instance)
        self.assertIsInstance(serializer_instance, serializers.ModelSerializer)
        self.assertEqual({"id": str(self.instance.id), "field": self.instance.field}, serializer_instance.data)

    def test_nested_serializer(self) -> None:
        """Test using the InlineSerializer as a Nested serializer."""
        children_instance = self.TestA_ChildConcreteModel._default_manager.create(parent=self.instance)

        class SerializerWithInlineChild(serializers.ModelSerializer[TestInlineSerializer.TestA_ConcreteModel]):
            children = InlineSerializer(self.TestA_ChildConcreteModel, ("id", "child_field"), many=True)

            class Meta:
                model = self.TestA_ConcreteModel
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
            SerializerClass = InlineSerializer(self.TestA_ConcreteModel, ("id", "field"))
            self.assertEqual(
                SerializerClass.__name__,  # type: ignore[attr-defined]
                f"{self.TestA_ConcreteModel.__name__}InlineSerializer",
            )
        with self.subTest("Test custom name"):
            custom_name = uuid()
            SerializerClass = InlineSerializer(self.TestA_ConcreteModel, ("id", "field"), serializer_name=custom_name)
            self.assertEqual(
                SerializerClass.__name__,  # type: ignore[attr-defined]
                custom_name,
            )


class TestFilteredPrimaryKeyRelatedField(AbstractModelTestCase):
    """
    Test the FilteredPrimaryKeyRelatedField.

    Because all ConcreteModels need to be unique within "core", we prefix all of them with "TestB".
    """

    class TestB_ChildConcreteModel(AbstractBaseModel):
        filter = models.BooleanField()

        class Meta:
            # Because extensions is not an "installed_app", and related name needs a real installed app name.
            app_label = "core"

    class TestB_ParentConcreteModel(AbstractBaseModel):
        child = models.ForeignKey("TestB_ChildConcreteModel", on_delete=models.DO_NOTHING)

        class Meta:
            # Because extensions is not an "installed_app", and related name needs a real installed app name.
            app_label = "core"

    MODELS = (TestB_ChildConcreteModel, TestB_ParentConcreteModel)

    def test_filter(self) -> None:
        """Test that the queryset filtering works."""
        child = self.TestB_ChildConcreteModel._default_manager.create(filter=False)

        def filter_children(
            context: dict[str, Any],
            queryset: Optional[models.QuerySet[TestFilteredPrimaryKeyRelatedField.TestB_ChildConcreteModel]],
        ) -> models.QuerySet[TestFilteredPrimaryKeyRelatedField.TestB_ChildConcreteModel]:
            filter_value = context.get("filter_value", False)
            qs = queryset or self.TestB_ChildConcreteModel._default_manager.all()
            return qs.filter(filter=filter_value)

        class ParentSerializer(
            serializers.ModelSerializer[TestFilteredPrimaryKeyRelatedField.TestB_ParentConcreteModel]
        ):
            child = FilteredPrimaryKeyRelatedField(filter_queryset=filter_children)

            class Meta:
                model = self.TestB_ParentConcreteModel
                fields = ("id", "child")

        with self.subTest("Create with included child"):
            serializer = ParentSerializer(data={"child": child.id}, context={"filter_value": child.filter})
            self.assertTrue(serializer.is_valid())
            parent = serializer.save()
            self.assertEqual(child, parent.child)

        with self.subTest("Create with excluded child"):
            serializer = ParentSerializer(data={"child": child.id}, context={"filter_value": not child.filter})
            with self.assertRaises(ValidationError) as ctx:
                serializer.is_valid(raise_exception=True)
            self.assertEqual(ctx.exception.get_codes(), {"child": ["does_not_exist"]})


class TestNestedPrimaryKeyRelatedField(AbstractModelTestCase):
    """
    Test the NestedPrimaryKeyRelatedField.

    Because all ConcreteModels need to be unique within "core", we prefix all of them with "TestC".
    """

    class TestC_ChildConcreteModel(AbstractBaseModel):
        field1 = models.TextField(default="_field1")
        field2 = models.TextField(default="_field2")

        class Meta:
            # Because extensions is not an "installed_app", and related name needs a real installed app name.
            app_label = "core"

    class TestC_ParentConcreteModel(AbstractBaseModel):
        child = models.OneToOneField("TestC_ChildConcreteModel", on_delete=models.DO_NOTHING, related_name="reverse")

        class Meta:
            # Because extensions is not an "installed_app", and related name needs a real installed app name.
            app_label = "core"

    MODELS = (TestC_ChildConcreteModel, TestC_ParentConcreteModel)

    def setUp(self) -> None:
        class ChildSerializer(serializers.ModelSerializer[TestNestedPrimaryKeyRelatedField.TestC_ChildConcreteModel]):
            class Meta:
                model = self.TestC_ChildConcreteModel
                fields = ("field1", "field2")

        self.ChildSerializer = ChildSerializer

        class ParentSerializer(
            serializers.ModelSerializer[TestNestedPrimaryKeyRelatedField.TestC_ParentConcreteModel]
        ):
            child = NestedPrimaryKeyRelatedField(ChildSerializer)

            class Meta:
                model = self.TestC_ParentConcreteModel
                fields = ("child",)

        self.ParentSerializer = ParentSerializer

        return super().setUp()

    def test_creation(self) -> None:
        """Test using the serializer to create a parent instance."""
        child = self.TestC_ChildConcreteModel._base_manager.create()
        original_count = self.TestC_ParentConcreteModel._base_manager.count()
        serialized_parent = self.ParentSerializer(data={"child": child.pk})
        serialized_parent.is_valid(raise_exception=True)
        parent = serialized_parent.save()
        # Check that it was created correctly
        self.assertEqual(original_count + 1, self.TestC_ParentConcreteModel._base_manager.count())
        self.assertEqual(parent.child, child)

    def test_creation_nested_data_fails(self) -> None:
        """Test using the serializer to create a parent instance with nested data instead of id fails."""
        child = self.TestC_ChildConcreteModel._base_manager.create()
        serialized_child_data = self.ChildSerializer(child).data
        serialized_parent = self.ParentSerializer(data={"child": serialized_child_data})
        with self.assertRaises(ValidationError) as ctx:
            serialized_parent.is_valid(raise_exception=True)
        self.assertEqual(ctx.exception.get_codes(), {"child": ["invalid"]})

    def test_representation(self) -> None:
        """Test that retrieving the presentation will display the nested data."""
        child = self.TestC_ChildConcreteModel._base_manager.create()
        parent = self.TestC_ParentConcreteModel._base_manager.create(child=child)
        serialized_parent = self.ParentSerializer(parent)
        data = serialized_parent.data
        self.assertEqual(self.ChildSerializer(child).data, data["child"])
