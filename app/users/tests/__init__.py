from typing import Optional
from core.utilities import uuid
from core.utilities.test import clear_model_args
from users.models import User


# Keep some example passwords for tests.
# Note: if the validators change, these may need to be updated

VALID_PASSWORD = "Password1."

INVALID_PASSWORDS = [
    "inqlm",  # too short (random so it's not a "too common" error)
    "33431697",  # all numeric (random so it's not a "too common" error)
    "password",  # too common
    "@example.com",  # too similar to the valid_email
]

INVALID_PASSWORD = INVALID_PASSWORDS[0]


def generate_valid_email() -> str:
    """Auxiliary method to generate a unique valid email with the `example.com` domain."""
    return f"{uuid()}@example.com"


def sample_user(
    *,
    id: Optional[str] = None,
    email: Optional[str] = None,
    password: str = VALID_PASSWORD,
    is_staff: Optional[bool] = None,
    is_superuser: Optional[bool] = None,
) -> User:
    """
    Create a sample user with the following default values:
    - `id`: auto-generated
    - `email`: unique valid email
    - `password`: pre-defined valid password
    - `is_staff`: default value
    - `is_superuser`: default value
    """
    if email is None:
        email = generate_valid_email()
    return User.objects.create_user(
        **clear_model_args(id=id, email=email, password=password, is_staff=is_staff, is_superuser=is_superuser)
    )
