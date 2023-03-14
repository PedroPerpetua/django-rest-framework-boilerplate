from pathlib import Path
from typing import Any, Optional, Self, TypedDict


class ConfigDict(TypedDict):
    """TypedDict for the logging configDict."""

    version: int
    disable_existing_loggers: bool
    formatters: dict[str, dict]
    filters: dict[str, dict]
    handlers: dict[str, dict]
    root: dict[str, Any]
    loggers: dict[str, dict]


class LoggingConfigurationBuilder:
    def __init__(self, disable_existing_loggers: bool = False) -> None:
        """
        Create a building instance to build a logging configuration.

        The following methods are available:
        - `add_formatter`
        - `set_default_formatter`
        - `add_filter`
        - `add_handler`
        - `add_console_handler`
        - `add_file_handler`
        - `add_logger`
        - `modify_root_log`

        Once the configuration is complete, the Django setting `LOGGING` should be assigned to `<instance>.build()`.
        """
        self._data: ConfigDict = {
            "version": 1,
            "disable_existing_loggers": disable_existing_loggers,
            "formatters": {},
            "filters": {},
            "handlers": {},
            "root": {},
            "loggers": {},
        }
        self._default_formatter: Optional[str] = None

    def add_formatter(self, name: str, format: str, style: str = "{", **kwargs: Any) -> Self:
        """Add a formatter to the configuration."""
        kwargs.update({"format": format})
        kwargs.update({"style": style})
        self._data["formatters"].update({name: kwargs})
        return self

    def set_default_formatter(self, name: str) -> Self:
        """Set a default formatter to use for all handlers if none is passed."""
        if name not in self._data["formatters"]:
            raise ValueError(f"No formatter named {name} added.")
        self._default_formatter = name
        return self

    def add_filter(self, name: str, filter: str, **kwargs: Any) -> Self:
        """Add a filter to the configuration."""
        kwargs.update({"()": filter})
        self._data["filters"].update({name: kwargs})
        return self

    def add_handler(self, name: str, **kwargs: Any) -> Self:
        """
        Add a handler to the configuration. Data should be formatted as Django expects it. For more precise handlers,
        use the shortcut methods `add_console_handler` and `add_file_handler`. If a formatter is not passed and a
        default formatter is set, uses that one instead.
        """
        if self._default_formatter is not None:
            kwargs.setdefault("formatter", self._default_formatter)
        self._data["handlers"].update({name: kwargs})
        return self

    def add_console_handler(self, name: str, **kwargs: Any) -> Self:
        """Shortcut method to add a console handler using a StreamHandler."""
        kwargs.update({"class": "logging.StreamHandler"})
        return self.add_handler(name, **kwargs)

    def add_file_handler(self, name: str, file_path: Path | str, **kwargs: Any) -> Self:
        """Shortcut method to add a file handler using FileHandler."""
        # Create the parent folder if it doesn't exist
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        kwargs.update({"class": "logging.FileHandler"})
        kwargs.update({"filename": str(file_path)})
        return self.add_handler(name, **kwargs)

    def add_logger(self, name: str, handlers: list[str], **kwargs: Any) -> Self:
        """Add a logger to the configuration."""
        kwargs.update({"handlers": handlers})
        self._data["loggers"].update({name: kwargs})
        return self

    def modify_root_logger(self, **kwargs: Any) -> Self:
        """Modify the root logger configuration. This method only extends and overrides, does not delete."""
        self._data["root"].update(kwargs)
        return self

    def build(self) -> ConfigDict:
        """Return the LoggingConfiguration built and ready to be used by Django."""
        return self._data
