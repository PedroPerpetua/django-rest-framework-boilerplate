import json
from datetime import datetime
from typing import Any, Self
from unittest.mock import MagicMock, patch
from uuid import UUID
from django.db import models
from django.test import override_settings
from django.utils.timezone import make_aware
from extensions.models import mixins
from extensions.models.managers import SoftDeleteManager
from extensions.utilities import uuid
from extensions.utilities.test import AbstractModelTestCase, SampleFile


class TestUUIDPrimaryKeyMixin(AbstractModelTestCase):
    """Test the `UUIDPrimaryKeyMixin`."""

    class ConcreteModel(mixins.UUIDPrimaryKeyMixin, models.Model):
        class Meta:
            # Because extensions is not an "installed_app"
            app_label = uuid()

    MODELS = (ConcreteModel,)

    def test_create(self) -> None:
        """Test creating an instance of a model with the mixin."""
        obj = self.ConcreteModel._default_manager.create()
        self.assertIsNotNone(obj.id)
        self.assertIsInstance(obj.id, UUID)


class TestCreatedAtMixin(AbstractModelTestCase):
    """Test the `CreatedAtMixin`."""

    class ConcreteModel(mixins.CreatedAtMixin, models.Model):
        class Meta:
            # Because extensions is not an "installed_app"
            app_label = uuid()

    MODELS = (ConcreteModel,)

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
        class Meta:
            # Because extensions is not an "installed_app"
            app_label = uuid()

    MODELS = (ConcreteModel,)

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
        objects = SoftDeleteManager[Self]()

        class Meta:
            # Because extensions is not an "installed_app"
            app_label = uuid()

    MODELS = (ConcreteModel,)

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


@override_settings(DEBUG=True)
class TestExtendedReprMixin(AbstractModelTestCase):
    """Test the `ExtendedReprMixin`."""

    class ExtendedReprConcreteModel(mixins.ExtendedReprMixin, models.Model):
        class Choices(models.TextChoices):
            choice = "C", "choice"

        # Basic fields
        _char = models.CharField(max_length=255)
        _text = models.TextField()
        _int = models.IntegerField()
        _float = models.FloatField()
        _choices = models.CharField(max_length=1, choices=Choices.choices)
        _file = models.FileField()
        _boolean = models.BooleanField()
        _empty = models.IntegerField(null=True)

        # Relationships
        _one_to_one = models.OneToOneField(
            "ExtendedReprSimpleConcreteModel",
            on_delete=models.DO_NOTHING,
            related_name="_one_to_one_reverse",
        )
        _one_to_one_empty = models.OneToOneField(
            "ExtendedReprSimpleConcreteModel",
            null=True,
            on_delete=models.DO_NOTHING,
            related_name="_one_to_one_empty_reverse",
        )
        _fk = models.ForeignKey(
            "ExtendedReprSimpleConcreteModel",
            on_delete=models.DO_NOTHING,
            related_name="_fk_reverse",
        )
        _fk_empty = models.ForeignKey(
            "ExtendedReprSimpleConcreteModel",
            null=True,
            on_delete=models.DO_NOTHING,
            related_name="_fk_empty_reverse",
        )
        _m2m: Any = models.ManyToManyField("ExtendedReprSimpleConcreteModel", related_name="_m2m_reverse")
        _m2m_empty: Any = models.ManyToManyField("ExtendedReprSimpleConcreteModel", related_name="_m2m_empty_reverse")
        _recursive = models.ForeignKey(
            "SimpleRecursiveConcreteModel",
            on_delete=models.DO_NOTHING,
            related_name="_recursive_reverse",
        )

        class Meta:
            # Because extensions is not an "installed_app", and related name needs a real installed app name.
            app_label = "core"

    class ExtendedReprSimpleConcreteModel(mixins.ExtendedReprMixin, models.Model):
        _field = models.CharField(max_length=255, default="_field")

        class Meta:
            # Because extensions is not an "installed_app", and related name needs a real installed app name.
            app_label = "core"

    class SimpleRecursiveConcreteModel(models.Model):
        _related = models.ForeignKey(
            "ExtendedReprConcreteModel",
            null=True,
            on_delete=models.DO_NOTHING,
            related_name="_related_reverse",
        )

        class Meta:
            # Because extensions is not an "installed_app", and related name needs a real installed app name.
            app_label = "core"

    MODELS = (
        ExtendedReprConcreteModel,
        ExtendedReprSimpleConcreteModel,
        SimpleRecursiveConcreteModel,
    )

    def test_repr(self) -> None:
        """Test the `repr` of a model with the mixin."""
        simple_instance = self.ExtendedReprSimpleConcreteModel._default_manager.create()
        recursive_instance = self.SimpleRecursiveConcreteModel._default_manager.create()

        # Create the object
        obj = self.ExtendedReprConcreteModel._default_manager.create(
            _char="_char",
            _text="_text",
            _int=1,
            _float=1.0,
            _choices=self.ExtendedReprConcreteModel.Choices.choice,
            _file=SampleFile(),
            _boolean=True,
            _empty=None,
            _one_to_one=simple_instance,
            _one_to_one_empty=None,
            _fk=simple_instance,
            _fk_empty=None,
            _recursive=recursive_instance,
        )
        # Set the M2M
        obj._m2m.add(simple_instance)
        # Set the recursive back
        recursive_instance._related = obj
        recursive_instance.save()

        # Make the call and check
        repr_str = repr(obj)
        # The repr should be able to be parsed as JSON
        repr_obj = json.loads(repr_str)

        # Check that the simple instance gets serialized correctly (ignoring the object)
        simple_instance_repr_data = mixins.ExtendedReprMixin._get_repr_data(simple_instance, [obj])
        self.assertEqual(
            {
                "model": simple_instance.__class__.__name__,
                "pk": simple_instance.pk,
                "id": simple_instance.id,  # type: ignore[attr-defined] # auto generated
                "_field": simple_instance._field,
                "_one_to_one_reverse": mixins.ExtendedReprMixin._get_short_repr_data(obj),
                "_fk_reverse": [mixins.ExtendedReprMixin._get_short_repr_data(obj)],
                "_fk_empty_reverse": [],
                "_m2m_reverse": [mixins.ExtendedReprMixin._get_short_repr_data(obj)],
                "_m2m_empty_reverse": [],
            },
            simple_instance_repr_data,
        )

        # Check the basic information
        self.assertEqual(obj.__class__.__name__, repr_obj["model"])
        self.assertEqual(obj.pk, repr_obj["pk"])
        self.assertEqual(obj.id, repr_obj["id"])  # type: ignore[attr-defined] # auto generated

        # Check the basic fields
        self.assertEqual(obj._char, repr_obj["_char"])
        self.assertEqual(obj._text, repr_obj["_text"])
        self.assertEqual(obj._int, repr_obj["_int"])
        self.assertEqual(obj._float, repr_obj["_float"])
        self.assertEqual(obj.get__choices_display(), repr_obj["_choices"])  # type: ignore[attr-defined] # auto generated
        self.assertEqual(obj._file.path, repr_obj["_file"])
        self.assertEqual(obj._boolean, repr_obj["_boolean"])
        self.assertEqual(obj._empty, repr_obj["_empty"])

        # Check the relationships
        self.assertEqual(simple_instance_repr_data, repr_obj["_one_to_one"])
        self.assertEqual(obj._one_to_one_empty, repr_obj["_one_to_one_empty"])
        self.assertEqual(simple_instance_repr_data, repr_obj["_fk"])
        self.assertURLEqual(obj._fk_empty, repr_obj["_fk_empty"])
        self.assertEqual([simple_instance_repr_data], repr_obj["_m2m"])
        self.assertEqual(list(obj._m2m_empty.iterator()), repr_obj["_m2m_empty"])

        # Check the recursive model
        recursive_instance_repr_data = mixins.ExtendedReprMixin._get_repr_data(recursive_instance, [obj])
        self.assertEqual(
            {
                "model": obj._recursive.__class__.__name__,
                "pk": obj._recursive.pk,
                "id": obj._recursive.id,
                "_recursive_reverse": [obj._get_short_repr_data(obj)],
                "_related": obj._get_short_repr_data(obj),
            },
            recursive_instance_repr_data,
        )
        self.assertEqual(recursive_instance_repr_data, repr_obj["_recursive"])
        self.assertEqual([recursive_instance_repr_data], repr_obj["_related_reverse"])

    @patch("extensions.models.mixins.getattr")
    def test_recursion_error(self, getattr_mock: MagicMock) -> None:
        """Test that if a recursion error is hit inside the data, the simplest representation will be returned."""
        # Setup the mock
        getattr_mock.side_effect = RecursionError()

        # Create the object
        obj = self.ExtendedReprSimpleConcreteModel._default_manager.create()

        # Make the call and check
        repr_str = repr(obj)
        # The repr should be able to be parsed as JSON
        repr_obj = json.loads(repr_str)
        self.assertEqual(mixins.ExtendedReprMixin._get_short_repr_data(obj), repr_obj)

    @override_settings(DEBUG=False)
    def test_debug_off_db_hits(self) -> None:
        """Tests that when Debug mode is off, we don't query the DB for the related objects."""

        simple_instance = self.ExtendedReprSimpleConcreteModel._default_manager.create()
        recursive_instance = self.SimpleRecursiveConcreteModel._default_manager.create()

        # Create the object
        obj = self.ExtendedReprConcreteModel._default_manager.create(
            _char="_char",
            _text="_text",
            _int=1,
            _float=1.0,
            _choices=self.ExtendedReprConcreteModel.Choices.choice,
            _file=SampleFile(),
            _boolean=True,
            _empty=None,
            _one_to_one=simple_instance,
            _one_to_one_empty=None,
            _fk=simple_instance,
            _fk_empty=None,
            _recursive=recursive_instance,
        )
        # Set the M2M
        obj._m2m.add(simple_instance)
        # Set the recursive back
        recursive_instance._related = obj
        recursive_instance.save()

        # Should do 0 queries and return the short representation
        with self.assertNumQueries(0):
            repr_str = repr(obj)
        # The repr should be able to be parsed as JSON
        repr_obj = json.loads(repr_str)
        self.assertEqual(mixins.ExtendedReprMixin._get_short_repr_data(obj), repr_obj)
