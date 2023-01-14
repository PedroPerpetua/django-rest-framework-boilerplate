from typing import Optional
from core.utilities import uuid
from core.utilities.test import clear_model_args
from users.models import User


def sample_user(
    *,
    id: Optional[str] = None,
    email: Optional[str] = None,
    password: Optional[str] = None,
    is_staff: Optional[bool] = None,
    is_superuser: Optional[bool] = None
) -> User:
    """
    Create a sample user with the following default values:
    - `id`: auto-generated
    - `email`: "<uuid>@example.com"
    - `password`: unique valid password
    - `is_staff`: default value
    - `is_superuser`: default value
    """
    if password is None:
        password = generate_valid_password()
    if email is None:
        email = f"{uuid()}@example.com"
    return User.objects.create_user(
        **clear_model_args(id=id, email=email, password=password, is_staff=is_staff, is_superuser=is_superuser)
    )


def generate_valid_password() -> str:
    """Auxiliary method to generate a unique password that obeys our set password validations."""
    return uuid()


def generate_invalid_password() -> str:
    """Auxiliary method to generate a password that will be too weak for our set password validations."""
    return "weak"
