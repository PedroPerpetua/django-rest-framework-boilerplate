from __future__ import annotations
from pathlib import Path
from typing import Any, Callable
from uuid import uuid4


def uuid() -> str:
    """Generate a random uuid4. This is a shorthand; equivalent to `str(uuid4())`."""
    return str(uuid4())


class Singleton[T](type):
    """A metaclass to apply the Singleton pattern."""

    _instances: dict[Singleton[T], T] = {}

    def __call__(cls, *args: Any, **kwds: Any) -> T:
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwds)
        return cls._instances[cls]


class _Undefined(metaclass=Singleton):
    """
    This class represents an Undefined value. We use it to specify defaults for arguments that can take `None` as
    their value, so that we don't mix the two.

    Should be used together with the `clear_Undefined` function.

    This is a singleton class; instances will always evaluate to `False`, and comparisons will always evaluate to
    `False`.
    """

    def __eq__(self, _: Any) -> bool:
        return False

    def __bool__(self) -> bool:
        return False


Undefined = _Undefined()
"""Singleton of the `_Undefined` class."""

type Undefinable[T] = _Undefined | T
"""Similar to `Optional`, but with `_Undefined`"""


def clear_Undefined(**kwargs: Any) -> dict[str, Any]:
    """
    Clear out `Undefined` objects from the passed kwargs and return the rest.

    This function is very useful as a way to "delete" items from kwargs as they're passed down to model object
    creation; we avoid using `None` because some models do take `None` as an option.
    """
    return {k: v for k, v in kwargs.items() if not isinstance(v, _Undefined)}


def ext(filename: str, leading_dot: bool = False) -> str:
    """
    Given a filename, returns the extension.

    If leading_dot is true and there is an extension, will return the leading dot along the extensions.
    """
    extensions = "".join(Path(filename).suffixes)
    if leading_dot or len(extensions) == 0:
        return extensions
    return extensions[1:]


def order_list[T](original: list[T], ordering: list[str], func: Callable[[T], str] = lambda x: str(x)) -> list[T]:
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
