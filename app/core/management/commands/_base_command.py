from __future__ import annotations
from typing import Any
from django.core.management.base import BaseCommand as DjangoCommand
from django.core.management.base import OutputWrapper


class BaseCommand(DjangoCommand):
    """
    Base class for commands with shortcuts for info, success, warning and error messages.

    Also has a `get_indented_streams` method that returns output streams with one more indentation level.
    """

    class IndentedOutputWrapper(OutputWrapper):
        """Wrapper around Django's commands OutputWrappers to support incremental indentation levels."""

        _level: int
        INDENTATION = " " * 2  # 2 spaces

        def __init__(self, source: OutputWrapper | BaseCommand.IndentedOutputWrapper):
            out_source = source if not isinstance(source, OutputWrapper) else source._out
            super().__init__(out=out_source, ending="")  # type: ignore[arg-type] # Supertype "incompatibility"
            self._level = 1
            if hasattr(source, "_level") and isinstance(source._level, int):
                self._level = source._level + 1
            self.style_func = None  # type: ignore[assignment] # Setting 'None' sets it to the default style_func
            if hasattr(source, "style_func"):
                self.style_func = source.style_func

        def write(self, msg: str = "", *args: Any, **kwargs: Any) -> None:  # type: ignore[override]
            msg = self.INDENTATION * self._level + msg
            return super().write(msg, *args, **kwargs)

    def get_indented_streams(self, kwargs: dict[Any, Any]) -> tuple[IndentedOutputWrapper, IndentedOutputWrapper]:
        """Returns stdout and stderr streams with one more indentation level."""
        stdout = kwargs.pop("stdout", self.stdout)
        stderr = kwargs.pop("stderr", self.stderr)
        return (self.IndentedOutputWrapper(stdout), self.IndentedOutputWrapper(stderr))

    def info(self, message: str) -> None:
        """Print the message to stdout with HTTP_INFO style."""
        self.stdout.write(self.style.HTTP_INFO(message))

    def success(self, message: str) -> None:
        """Print the message to stdout with SUCCESS style."""
        self.stdout.write(self.style.SUCCESS(message))

    def warning(self, message: str) -> None:
        """Print the message to stderr with WARNING style."""
        self.stderr.write(self.style.WARNING(message))

    def error(self, message: str) -> None:
        """Print the message to stderr with ERROR style."""
        self.stderr.write(self.style.ERROR(message))
