from typing import Optional
from django.contrib.auth.models import AbstractBaseUser
from django.core.exceptions import ValidationError
from core.utilities import clear_Nones, uuid
from core.utilities.test import AbstractModelTestCase
from users.abstract_models import UserEmailMixin, UserUsernameMixin
from users.models import UserManager
from users.tests import VALID_PASSWORD, generate_valid_email


class TestAbstractUserWithEmail(AbstractModelTestCase):
    class UserWithEmail(UserEmailMixin, AbstractBaseUser):
        USERNAME_FIELD = "email"
        objects = UserManager()

    MODEL = UserWithEmail

    def sample_user(
        self,
        *,
        id: Optional[str] = None,
        email: Optional[str] = None,
        password: str = VALID_PASSWORD,
        is_staff: Optional[bool] = None,
        is_superuser: Optional[bool] = None,
        is_active: Optional[bool] = None,
    ) -> UserWithEmail:
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
        return self.UserWithEmail.objects.create_user(  # type: ignore # We use the same manager that returns User
            **clear_Nones(
                id=id,
                email=email,
                password=password,
                is_staff=is_staff,
                is_superuser=is_superuser,
                is_active=is_active,
            )
        )

    def test_create_user(self) -> None:
        """Test creating a UserWithEmail."""
        email = generate_valid_email()
        password = VALID_PASSWORD
        user = self.UserWithEmail.objects.create_user(email=email, password=password)
        self.assertEqual(email, user.get_username())
        self.assertEqual(email, user.email)
        self.assertNotEqual(password, user.password)
        self.assertTrue(user.check_password(password))

    def test_email_required(self) -> None:
        """Test creating a UserWithEmail without an email fails."""
        with self.assertRaises(ValidationError) as ctx:
            self.UserWithEmail.objects.create_user(password=VALID_PASSWORD)
        self.assertIn(ValidationError("Email cannot be empty."), ctx.exception.error_list)

    def test_email_invalid_fails(self) -> None:
        """Test creating a UserWithEmail with an invalid email fails."""
        with self.assertRaises(ValidationError) as ctx:
            self.UserWithEmail.objects.create_user(email="_invalid_email", password=VALID_PASSWORD)
        self.assertIn(ValidationError("Email is invalid."), ctx.exception.error_list)

    def test_email_normalized(self) -> None:
        """Test that emails are normalized for UserWithEmail."""
        sample_emails = [
            ("test1@EXAMPLE.com", "test1@example.com"),
            ("TEST2@example.com", "TEST2@example.com"),
            ("TEST3@EXAMPLE.com", "TEST3@example.com"),
            ("test4@example.COM", "test4@example.com"),
        ]
        for email, expected in sample_emails:
            with self.subTest(msg="Checking if email is normalized.", email=email, expected=expected):
                user = self.sample_user(email=email)
                self.assertEqual(expected, user.email)

    def test_email_changes_normalized(self) -> None:
        """Test that emails are normalized when updating a user."""
        user = self.sample_user()
        email, expected = ("test1@EXAMPLE.com", "test1@example.com")
        user.email = email
        user.save()
        self.assertEqual(expected, user.email)


class TestAbstractUserWithUsername(AbstractModelTestCase):
    class UserWithUsername(UserUsernameMixin, AbstractBaseUser):
        USERNAME_FIELD = "username"
        objects = UserManager()

    MODEL = UserWithUsername

    def sample_user(
        self,
        *,
        id: Optional[str] = None,
        username: Optional[str] = None,
        password: str = VALID_PASSWORD,
        is_staff: Optional[bool] = None,
        is_superuser: Optional[bool] = None,
        is_active: Optional[bool] = None,
    ) -> UserWithUsername:
        """
        Create a sample user with the following default values:
        - `id`: auto-generated
        - `username`: unique username
        - `password`: pre-defined valid password
        - `is_staff`: default value
        - `is_superuser`: default value
        """
        if username is None:
            username = uuid()
        return self.UserWithUsername.objects.create_user(  # type: ignore # We use the same manager that returns User
            **clear_Nones(
                id=id,
                username=username,
                password=password,
                is_staff=is_staff,
                is_superuser=is_superuser,
                is_active=is_active,
            )
        )

    def test_create_user(self) -> None:
        """Test creating a UserWithUsername."""
        username = uuid()
        password = VALID_PASSWORD
        user = self.UserWithUsername.objects.create_user(username=username, password=password)
        self.assertEqual(username, user.get_username())
        self.assertEqual(username, user.username)
        self.assertNotEqual(password, user.password)
        self.assertTrue(user.check_password(password))

    def test_username_required(self) -> None:
        """Test creating a UserWithUsername without a username fails."""
        with self.assertRaises(ValidationError) as ctx:
            self.UserWithUsername.objects.create(password=VALID_PASSWORD)
        self.assertIn(ValidationError("Username cannot be empty."), ctx.exception.error_list)
