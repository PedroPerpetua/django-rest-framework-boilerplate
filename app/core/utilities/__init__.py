from __future__ import annotations  # Required by the `if TYPE_CHECKING` block
import xml.etree.cElementTree as et
from io import TextIOWrapper
from pathlib import Path
from typing import TYPE_CHECKING, Any, Optional, overload
from uuid import uuid4
from django.core.files import File


if TYPE_CHECKING:
    """
    We only import this when typechecking to prevent DRF from being loaded into this module, as our `settings.py` file
    imports from this module to setup. If we import this regularly, we're met with an issue where DRF is loaded BEFORE
    `REST_FRAMEWORK` settings are set, causing them to never be loaded at all.
    """
    from core.utilities.types import JSON_BASE


def uuid() -> str:
    """Generate a random uuid4. This is a shorthand; equivalent to `str(uuid4())`."""
    return str(uuid4())


def empty(string: Optional[str]) -> bool:
    """Given a string, returns True if it's None or empty, or only whitespace."""
    if not string:
        return True
    if string.strip() == "":
        return True
    return False


@overload
def clear_Nones(**kwargs: Any) -> dict[str, Any]:
    ...


@overload
def clear_Nones(json_obj: JSON_BASE, **kwargs: Any) -> JSON_BASE:
    ...


def clear_Nones(json_obj: Optional[JSON_BASE] = None, **kwargs: Any) -> JSON_BASE:
    """Clear an object intended to be serialized as JSON by removing all `None` values, recursively."""
    if json_obj is None:
        return clear_Nones(kwargs)
    if isinstance(json_obj, dict):
        json_obj.update(kwargs)
        return {k: clear_Nones(v) for k, v in json_obj.items() if v is not None}
    if isinstance(json_obj, list):
        return [clear_Nones(v) for v in json_obj if v is not None]
    return json_obj


def ext(filename: str, leading_dot: bool = False) -> str:
    """
    Given a filename, returns the extension.

    If leading_dot is true and there is an extension, will return the leading dot along the extensions.
    """
    extensions = "".join(Path(filename).suffixes)
    if leading_dot or len(extensions) == 0:
        return extensions
    return extensions[1:]
