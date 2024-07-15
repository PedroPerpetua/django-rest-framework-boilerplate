from django.db import models
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.utils.serializer_helpers import ReturnDict
from extensions.models import AbstractBaseModel
from extensions.serializers import NestedPrimaryKeyRelatedField
from extensions.utilities.test import AbstractModelTestCase


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

    MODELS = [ConcreteChildModel, ConcreteParentModel]

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
        exc_detail: ReturnDict = ctx.exception.detail  # type: ignore
        self.assertIn("child", exc_detail.keys())
        self.assertEqual("invalid", exc_detail["child"][0].code)

    def test_representation(self) -> None:
        """Test that retrieving the presentation will display the nested data."""
        child = self.ConcreteChildModel._base_manager.create()
        parent = self.ConcreteParentModel._base_manager.create(child=child)
        serialized_parent = self.parentSerializer(parent)
        data = serialized_parent.data
        self.assertEqual(self.childSerializer(child).data, data["child"])
