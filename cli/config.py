import tomllib
from typing import Any
from cli.files import PYPROJECT_FILE


class Config(dict[str, Any]):
    """Recursive dict that will always return an empty dict if a key doesn't exist."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Override the init so we recursively re-do dictionary values"""
        super().__init__(*args, **kwargs)
        for key, value in self.items():
            if not isinstance(value, dict):
                continue
            self[key] = Config(value)

    def __missing__(self, key: str) -> Any:
        self[key] = Config()
        return self[key]


def load_config(*, raise_exception: bool = True) -> Config:
    if not PYPROJECT_FILE.exists():
        if raise_exception:
            raise FileNotFoundError(f"Config file {PYPROJECT_FILE.as_posix()} not found.")
        return Config()
    try:
        with open(PYPROJECT_FILE, "rb") as config_file:
            return Config(tomllib.load(config_file))
    except:
        if raise_exception:
            raise
        return Config()
