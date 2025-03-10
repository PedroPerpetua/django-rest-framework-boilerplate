from typing import Optional
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import AnonymousUser
from users.models import User


class AuthenticationBackend(ModelBackend):
    """Custom authentication backend that also checks for the User's `is_deleted` status."""

    def user_can_authenticate(self, user: Optional[User | AnonymousUser]) -> bool:
        """Override this method so that we can check for the `is_deleted` status."""
        if not super().user_can_authenticate(user):
            return False
        return not getattr(user, "is_deleted", False)
