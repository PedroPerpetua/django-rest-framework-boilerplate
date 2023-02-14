from typing import Literal, Optional
from core.utilities import clear_Nones, uuid
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


def generate_valid_username(field_name: Literal["username", "email"] | str) -> str:
    """
    Auxiliary method to generate a unique valid string for the corresponding `field_name`. Supports `email` and
    `username`. If the `field_name` has another value, raises `AssertionError`.
    """
    match field_name:  # pragma: no cover
        case "email":
            return generate_valid_email()
        case "username":
            return uuid()
        case _:
            raise AssertionError(f"Unrecognized username field: {field_name}")


def sample_user(
    *,
    id: Optional[str] = None,
    username: Optional[str] = None,
    email: Optional[str] = None,
    password: str = VALID_PASSWORD,
    is_staff: Optional[bool] = None,
    is_superuser: Optional[bool] = None,
    is_active: Optional[bool] = None,
) -> User:
    """
    Create a sample user with the following default values:
    - `id`: auto-generated
    - `username`: unique username, if the User model has a username.
    - `email`: unique valid email, if the User model has an email.
    - `password`: pre-defined valid password
    - `is_staff`: default value
    - `is_superuser`: default value
    """
    if username is None and hasattr(User, "username"): # pragma: no cover
        username = uuid()
    if email is None and hasattr(User, "email"): # pragma: no cover
        email = generate_valid_email()
    return User.objects.create_user(
        **clear_Nones(
            id=id,
            username=username,
            email=email,
            password=password,
            is_staff=is_staff,
            is_superuser=is_superuser,
            is_active=is_active,
        )
    )
