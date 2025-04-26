from rest_framework.generics import GenericAPIView
from users.models import User


class TargetAuthenticatedUserMixin(GenericAPIView[User]):
    """Mixin for views that target the authenticated user."""

    def get_object(self) -> User:
        assert isinstance(self.request.user, User)
        return self.request.user
