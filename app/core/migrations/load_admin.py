"""
This migration will create a super user when migrations are applied based on
the project settings.

Taken from: https://stackoverflow.com/questions/6244382/
"""
import os
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import migrations
from django.db.backends.base.schema import BaseDatabaseSchemaEditor


class Migration(migrations.Migration):
    initial = True

    def generate_superuser(self, schema_editor: BaseDatabaseSchemaEditor) -> None:
        from django.contrib.auth.models import User
        ENV = os.environ

        if get_user_model() != User:
            # If the default user model has been overridden, this migration should be adjusted and this check removed.
            raise Exception("Default user module overridden! Invalid Migration.")
        superuser = User.objects.create_superuser(
            username=ENV["ADMIN_USERNAME"],
            email=ENV["ADMIN_EMAIL"],
            password=ENV["ADMIN_PASSWORD"]
        )
        superuser.save()

    operations = [
        migrations.RunPython(generate_superuser),  # type: ignore
    ]
