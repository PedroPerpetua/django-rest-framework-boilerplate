from uuid import UUID
from extensions.utilities import Undefinable, Undefined, clear_Undefined, uuid
from users.models import User


VALID_PASSWORD = "Password1."
"""Valid password to use in tests. If the password requirements change, may need to be updated."""


def sample_user(
    *,
    id: Undefinable[UUID | str] = Undefined,
    username: Undefinable[str] = Undefined,
    password: Undefinable[str] = Undefined,
    is_staff: Undefinable[bool] = Undefined,
    is_superuser: Undefinable[bool] = Undefined,
    is_active: Undefinable[bool] = Undefined,
    is_deleted: Undefinable[bool] = Undefined,
) -> User:
    """
    Create a sample user with the following default values:
    - `id`: auto-generated
    - `username`: unique username
    - `password`: default value (no password)
    - `is_staff`: default value
    - `is_superuser`: default value
    - `is_active`: default value
    - `is_deleted`: default value
    """
    username = username or uuid()
    return User.objects.create_user(
        **clear_Undefined(
            id=id,
            username=username,
            password=password,
            is_staff=is_staff,
            is_superuser=is_superuser,
            is_active=is_active,
            is_deleted=is_deleted,
        )
    )
