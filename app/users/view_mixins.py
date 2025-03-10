from typing import cast
from extensions.utilities.types import GenericViewMixin
from users.models import User


class TargetAuthenticatedUserMixin(GenericViewMixin):
    """Mixin for views that target the authenticated user."""

    def get_object(self) -> User:
        return cast(User, self.request.user)
