from typing import Any
from django.conf import settings
from django.core.management.commands.startapp import Command as StartAppCommand


class Command(StartAppCommand):
    """Customize the StartAppCommand to use our custom app template by default."""

    TEMPLATE_PATH = settings.BASE_DIR / "core" / "app_template"

    def handle(self, *args: Any, **options: Any) -> None:
        """Override the `handle` method to add the option "template" with our template if None were passed."""
        if options.get("template", None) is None:
            options["template"] = str(self.TEMPLATE_PATH)
        return super().handle(*args, **options)
