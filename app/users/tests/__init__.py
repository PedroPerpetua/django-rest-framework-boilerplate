from typing import Optional
from core.utilities import clear_Nones, uuid
from users.models import User


VALID_PASSWORD = "Password1."
"""Valid password to use in tests. If the password requirements change, may need to be updated."""


def sample_user(
    *,
    id: Optional[str] = None,
    username: Optional[str] = None,
    password: Optional[str] = None,
    is_staff: Optional[bool] = None,
    is_superuser: Optional[bool] = None,
    is_active: Optional[bool] = None,
) -> User:
    """
    Create a sample user with the following default values:
    - `id`: auto-generated
    - `username`: unique username
    - `password`: pre-defined valid password
    - `is_staff`: default value
    - `is_superuser`: default value
    """
    username = username or uuid()
    password = password or VALID_PASSWORD
    return User.objects.create_user(
        **clear_Nones(
            id=id,
            username=username,
            password=password,
            is_staff=is_staff,
            is_superuser=is_superuser,
            is_active=is_active,
        )
    )
