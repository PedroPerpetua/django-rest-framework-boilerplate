import os
from typing import Optional


ENV = os.environ


def _get_value[T](var: str, default: Optional[T] = None) -> str | T:
    try:
        value = ENV[var]
        # We take defaults if available for empty values
        if len(value) == 0 and default is not None:
            return default
        return value
    except KeyError:
        if default is None:
            raise
        return default


def as_string(var: str, default: Optional[str] = None) -> str:
    """
    Return the environment variable as a string. If no default value is given and the variable is not set, raises
    KeyError.
    """
    return _get_value(var, default)


def as_int(var: str, default: Optional[int] = None) -> int:
    """
    Return the environment variable as an integer. If no default value is given and the variable is not set, raises
    KeyError.
    """
    return int(_get_value(var, default))


def as_bool(var: str, default: Optional[bool] = None) -> bool:
    """
    Return the environment variable as a boolean. We accept "true", "True", (etc), "t", "T", "1" as `True`, and
    everything else as `False`. If no default value is given and the variable is not set, raises Keyerror.
    """
    value = _get_value(var, default)
    if isinstance(value, str):
        return value.lower() in ["true", "1", "t"]
    return value


def as_list(var: str, default: Optional[list[str]] = None) -> list[str]:
    """
    Return the environment variable as a list of strings (previously separated by commas). If no default value is
    given and the variable is not set, raises KeyError.
    """
    value = _get_value(var, default)
    if isinstance(value, str):
        # Strip all values and remove empty ones
        values = value.split(",")
        retval: list[str] = []
        for val in values:
            v = val.strip()
            if v:
                retval.append(v)
        return retval
    return value
