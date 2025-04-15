from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable, Optional, TypeVar, overload
from uuid import uuid4


if TYPE_CHECKING:
    """
    We only import this when typechecking to prevent DRF from being loaded into this module, as our `settings.py` file
    imports from this module to setup. If we import this regularly, we're met with an issue where DRF is loaded BEFORE
    `REST_FRAMEWORK` settings are set, causing them to never be loaded at all.
    """
    from extensions.utilities.types import JSON

else:
    JSON = Any


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
def clear_Nones(**kwargs: Any) -> dict[str, Any]: ...


@overload
def clear_Nones(json_obj: Optional[JSON] = ..., **kwargs: Any) -> JSON: ...


def clear_Nones(json_obj: Optional[JSON] = None, **kwargs: Any) -> JSON:
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


T = TypeVar("T")


def order_list(original: list[T], ordering: list[str], func: Callable[[T], str] = lambda x: str(x)) -> list[T]:
    """
    This function will order a list (original) according to another list (ordering).

    The ordering list is a list of strings; if the original list is not a list of strings, their values will be
    converted to a string. If you need a custom conversion function, you can pass a third parameter (func) with a
    function that will map an element from the original list to a string.

    Items that are in the original but not in the ordering list will be appended at the end.
    """
    retval: list[T | None] = [None for _ in ordering]
    unordered: list[T] = []  # Store the values not in ordering to append at the end
    for value in original:
        # Check if it's in the list
        try:
            index = ordering.index(func(value))
            retval[index] = value
        except ValueError:
            unordered.append(value)
    return [v for v in retval if v is not None] + unordered
