"""
This migration will create a super user when migrations are applied based on
the project settings.

Taken from: https://stackoverflow.com/questions/6244382/
"""
from django.contrib.auth import get_user_model
from django.db import migrations
from django.db.backends.base.schema import BaseDatabaseSchemaEditor
from core.utilities import env


class Migration(migrations.Migration):
    initial = True

    # Make sure we always have the most recent user model.
    dependencies = [("users", "__latest__")]

    def generate_superuser(self, schema_editor: BaseDatabaseSchemaEditor) -> None:
        credentials = env.as_json("ADMIN_CREDENTIALS")
        if not isinstance(credentials, dict):  # pragma: no cover
            raise ValueError("ADMIN_CREDENTIALS must be a dictionary.")
        get_user_model().objects.create_superuser(**credentials)

    operations = [
        migrations.RunPython(generate_superuser),  # type: ignore
    ]
