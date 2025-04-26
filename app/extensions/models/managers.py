from django.db import models
from extensions.models.mixins import SoftDeleteMixin


class SoftDeleteManager[T: SoftDeleteMixin](models.Manager[T]):
    """
    Custom manager for models that implement the `SoftDeleteMixin`. Includes a method `exclude_deleted` to return the
    queryset with the soft deleted models filtered out.
    """

    def exclude_deleted(self) -> models.QuerySet[T]:
        """Return this model's queryset, with soft-deleted instances included."""
        return super().get_queryset().filter(is_deleted=False)
