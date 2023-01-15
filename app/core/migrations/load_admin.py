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

    def generate_superuser(self, schema_editor: BaseDatabaseSchemaEditor) -> None:
        get_user_model().objects.create_superuser(
            email=env.as_string("ADMIN_EMAIL"),
            password=env.as_string("ADMIN_PASSWORD"),
        )

    operations = [
        migrations.RunPython(generate_superuser),  # type: ignore
    ]
