from typing import Optional
from core.utilities import uuid
from core.utilities.test import clear_model_args
from users.models import User


def sample_user(
    *,
    id: Optional[str] = None,
    email: Optional[str] = None,
    password: str = "_password",
    is_staff: Optional[bool] = None
) -> User:
    """
    Create a sample user with the following default values:
    - id: auto-generated
    - `email`: "<uuid>@example.com"
    - password: "_password"
    - is_staff: default value
    """
    if email is None:
        email = f"{uuid()}@example.com"
    return User.objects.create(**clear_model_args(id=id, email=email, password=password, is_staff=is_staff))
