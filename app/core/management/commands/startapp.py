from pathlib import Path
from typing import Any, Optional
from django.conf import settings
from django.core.management.commands.startapp import Command as StartAppCommand


class Command(StartAppCommand):
    """Customize the StartAppCommand to use our custom app template by default."""

    TEMPLATE_PATH: Path = settings.BASE_DIR / "core" / "app_template"

    # https://github.com/typeddjango/django-stubs/issues/1820
    def handle(self, *args: Any, **options: Any) -> Optional[str]:  # type: ignore
        """Override the `handle` method to add the option "template" with our template if None were passed."""
        if options.get("template", None) is None:
            options["template"] = str(self.TEMPLATE_PATH)
        return super().handle(*args, **options)
