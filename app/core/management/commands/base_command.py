from django.core.management.base import BaseCommand as DjangoCommand


class BaseCommand(DjangoCommand):
    """
    Base class for commands with shortcuts for info, success, warning and
    error messages.
    """
    def info(self, message: str):
        """Print the message to stdout with HTTP_INFO style."""
        self.stdout.write(self.style.HTTP_INFO(message))

    def success(self, message: str):
        """Print the message to stdout with SUCCESS style."""
        self.stdout.write(self.style.SUCCESS(message))

    def warning(self, message: str):
        """Print the message to stderr with WARNING style."""
        self.stderr.write(self.style.WARNING(message))

    def error(self, message: str):
        """Print the message to stderr with ERROR style."""
        self.stderr.write(self.style.ERROR(message))
