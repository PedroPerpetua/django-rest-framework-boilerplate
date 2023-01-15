from uuid import uuid4
from django.db import models


class BaseAbstractModel(models.Model):
    """
    Base abstract model that features a base model with common fields, such as:
    - `created_at`
    - `updated_at`
    - `is_deleted`

    Also uses a UUID as primary key.
    """
    id = models.UUIDField(primary_key=True, unique=True, default=uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        abstract = True
        ordering = ['-created_at']

    def soft_delete(self) -> None:
        """Soft delete this instance by marking `is_deleted` as `True`."""
        self.is_deleted = True
        self.save()

    def __repr__(self) -> str:
        """Base repr for children that adds the model and the attributes."""
        data = {"model": self.__class__.__name__}
        for field in self._meta.get_fields():
            try:
                data.update({field.name: getattr(self, field.name)})
            except AttributeError:
                # Field is in the meta but for some reason doens't have it
                continue
        return str(data)
