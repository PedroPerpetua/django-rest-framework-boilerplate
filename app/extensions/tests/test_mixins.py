from datetime import datetime
from typing import Self
from unittest.mock import MagicMock, patch
from uuid import UUID
from django.db import models
from django.utils.timezone import make_aware
from extensions.models import mixins
from extensions.models.managers import SoftDeleteManager
from extensions.utilities import uuid
from extensions.utilities.test import AbstractModelTestCase


class TestUUIDPrimaryKeyMixin(AbstractModelTestCase):
    """Test the `UUIDPrimaryKeyMixin`."""

    class ConcreteModel(mixins.UUIDPrimaryKeyMixin, models.Model):
        ...

        class Meta:
            # Because extensions is not an "installed_app"
            app_label = uuid()

    MODELS = [ConcreteModel]

    def test_create(self) -> None:
        """Test creating an instance of a model with the mixin."""
        obj = self.ConcreteModel._default_manager.create()
        self.assertIsNotNone(obj.id)
        self.assertIsInstance(obj.id, UUID)


class TestCreatedAtMixin(AbstractModelTestCase):
    """Test the `CreatedAtMixin`."""

    class ConcreteModel(mixins.CreatedAtMixin, models.Model):
        ...

        class Meta:
            # Because extensions is not an "installed_app"
            app_label = uuid()

    MODELS = [ConcreteModel]

    @patch("django.utils.timezone.now")
    def test_create(self, datetime_mock: MagicMock) -> None:
        """Test creating an instance of a model with the mixin."""
        created_dt = make_aware(datetime(1970, 1, 1))
        datetime_mock.return_value = created_dt
        obj = self.ConcreteModel._default_manager.create()
        self.assertEqual(created_dt, obj.created_at)

    @patch("django.utils.timezone.now")
    def test_is_created_only(self, datetime_mock: MagicMock) -> None:
        """Test the added field only sets a time at creation."""
        first_dt = make_aware(datetime(1970, 1, 1))
        second_dt = make_aware(datetime(1970, 1, 2))
        datetime_mock.side_effect = [first_dt, second_dt]
        obj = self.ConcreteModel._default_manager.create()
        self.assertEqual(first_dt, obj.created_at)  # Creation
        obj.save(force_update=True)
        obj.refresh_from_db()
        self.assertEqual(first_dt, obj.created_at)  # Didn't change


class TestUpdatedAtMixin(AbstractModelTestCase):
    """Test the `UpdatedAtMixin`."""

    class ConcreteModel(mixins.UpdatedAtMixin, models.Model):
        ...

        class Meta:
            # Because extensions is not an "installed_app"
            app_label = uuid()

    MODELS = [ConcreteModel]

    @patch("django.utils.timezone.now")
    def test_create(self, datetime_mock: MagicMock) -> None:
        """Test creating an instance of a model with the mixin."""
        updated_dt = make_aware(datetime(1970, 1, 1))
        datetime_mock.return_value = updated_dt
        obj = self.ConcreteModel._default_manager.create()
        self.assertEqual(updated_dt, obj.updated_at)

    @patch("django.utils.timezone.now")
    def test_is_updated(self, datetime_mock: MagicMock) -> None:
        """Test the added field updates time when changes happen."""
        first_dt = make_aware(datetime(1970, 1, 1))
        second_dt = make_aware(datetime(1970, 1, 2))
        datetime_mock.side_effect = [first_dt, second_dt]
        obj = self.ConcreteModel._default_manager.create()
        self.assertEqual(first_dt, obj.updated_at)  # Creation
        obj.save(force_update=True)
        obj.refresh_from_db()
        self.assertEqual(second_dt, obj.updated_at)  # Changed


class TestSoftDeleteMixin(AbstractModelTestCase):
    """Test the `SoftDeleteMixin`."""

    class ConcreteModel(mixins.SoftDeleteMixin, models.Model):
        ...

        objects = SoftDeleteManager[Self]()

        class Meta:
            # Because extensions is not an "installed_app"
            app_label = uuid()

    MODELS = [ConcreteModel]

    def test_create(self) -> None:
        """Test creating an instance of a model with the mixin."""
        obj = self.ConcreteModel._default_manager.create()
        self.assertFalse(obj.is_deleted)

    def test_soft_delete(self) -> None:
        """Test soft-deletion of an object."""
        obj = self.ConcreteModel._default_manager.create()
        obj.soft_delete()
        obj.refresh_from_db()
        self.assertTrue(obj.is_deleted)

    def test_manager_exclude_deleted(self) -> None:
        """Test that this method excludes soft-deleted instanced."""
        obj = self.ConcreteModel._default_manager.create(is_deleted=True)
        self.assertNotIn(obj, self.ConcreteModel._default_manager.exclude_deleted())  # type: ignore[attr-defined]


class TestExtendedReprMixin(AbstractModelTestCase):
    """Test the `ExtendedReprMixin`."""

    class ExtendedReprConcreteModel(mixins.ExtendedReprMixin, models.Model):
        field = models.TextField(default="_field")

        class Meta:
            # Because extensions is not an "installed_app", and related name needs a real installed app name.
            app_label = "core"

    class ExtendedReprConcreteRelatedModel(mixins.ExtendedReprMixin, models.Model):
        # A previous bug would generate a `RecursionError` on the `__repr__` with OneToOne fields
        # This model is here to test that it doesn't happen anymore
        related = models.OneToOneField(
            "ExtendedReprConcreteModel", on_delete=models.DO_NOTHING, related_name="reverse"
        )

        class Meta:
            # Because extensions is not an "installed_app", and related name needs a real installed app name.
            app_label = "core"

    MODELS = [ExtendedReprConcreteModel, ExtendedReprConcreteRelatedModel]

    def test_repr(self) -> None:
        """Test the `repr` of a model with the mixin."""
        field_value = "_field_value"
        obj = self.ExtendedReprConcreteModel._default_manager.create(field=field_value)
        self.assertEqual(
            str({"model": self.ExtendedReprConcreteModel.__name__, "id": obj.pk, "field": field_value}), repr(obj)
        )

    def test_related_recursion(self) -> None:
        """Assure that `repr` on a model with a OneToOneField doesn't generate a `RecursionError`."""
        obj = self.ExtendedReprConcreteModel._default_manager.create()
        related_obj = self.ExtendedReprConcreteRelatedModel._default_manager.create(related=obj)
        self.assertIn(f"'related': {repr(obj)}", repr(related_obj))
        self.assertIn(f"'reverse': '{self.ExtendedReprConcreteRelatedModel.__name__} ({related_obj.pk})'", repr(obj))
