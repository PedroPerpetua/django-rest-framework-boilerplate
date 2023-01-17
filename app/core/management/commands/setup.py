from typing import Any
from django.core.management import call_command
from core.management.commands._base_command import BaseCommand


class Command(BaseCommand):
    """
    Command to setup the production environment.

    Does the following:
    - Clears and re-collects all static files
    - Waits for database
    - Migrates
    """

    TASKS = [
        ("Collection static...", ("collectstatic", "--no-input", "--clear")),
        ("Waiting for DB connection...", ("wait_for_db",)),
        ("Migrating...", ("migrate",)),
    ]

    def handle(self, *args: Any, **kwargs: Any) -> None:
        self.info("Setting up app for production...")
        # Generate indented streams
        i_stdout, i_stderr = self.get_indented_streams(kwargs)
        task_count = len(self.TASKS)
        for i, (text, task) in enumerate(self.TASKS):
            self.info(f"{text} ({i}/{task_count})")
            call_command(*task, stdout=i_stdout, stderr=i_stderr, *args, **kwargs)
        self.success(f"Finished Setup! ({task_count}/{task_count})")
