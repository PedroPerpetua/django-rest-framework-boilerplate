import time
from typing import Any
from django.db import connections
from django.db.utils import OperationalError
from core.management.commands._base_command import BaseCommand


class Command(BaseCommand):
    """
    Django command to pause execution until a database connection is made available.

    Upon failure, waits RETRY_SECONDS second(s) and tries again.

    If MAX_RETRIES is hit, stops and prints an error.
    """

    RETRY_SECONDS = 1
    MAX_RETRIES = 10

    def handle(self, *args: Any, **kwargs: Any) -> None:
        self.info("Waiting for database connection...")
        retries = 0
        while True:
            try:
                if connections["default"]:
                    self.success("Database connection available!")
                    return
            except OperationalError:
                if retries == self.MAX_RETRIES:
                    self.error(f"Reached {self.MAX_RETRIES} retries with no database connection. Aborting.")
                    return
                self.error(f"Connection unavailable, waiting {self.RETRY_SECONDS} second(s)...")
                retries += 1
                time.sleep(self.RETRY_SECONDS)
