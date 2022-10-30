"""
This migration will create a super user when migrations are applied based on
the project settings.

Taken from: https://stackoverflow.com/questions/6244382/
"""
from django.conf import settings
from django.db import migrations
from django.db.backends.base.schema import BaseDatabaseSchemaEditor
from django.contrib.auth import get_user_model


class Migration(migrations.Migration):
    initial = True

    def generate_superuser(self, schema_editor: BaseDatabaseSchemaEditor):
        from django.contrib.auth.models import User

        if get_user_model() != User:
            # Safe guard. If the default user model has been overridden, this
            # migration should be adjusted and this check removed.
            raise Exception(
                "Default user module overridden! Invalid Migration."
            )
        superuser = User.objects.create_superuser(
            username=settings.ADMIN_USERNAME,
            email=settings.ADMIN_EMAIL,
            password=settings.ADMIN_PASSWORD
        )
        superuser.save()

    operations = [
        migrations.RunPython(generate_superuser),
    ]
