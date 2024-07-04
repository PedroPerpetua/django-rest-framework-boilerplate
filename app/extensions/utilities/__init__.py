from __future__ import annotations  # Required by the TYPE_CHECKING block
import json
from pathlib import Path
from typing import TYPE_CHECKING, Any, Optional, cast, overload
from uuid import uuid4
from django.core.serializers.json import DjangoJSONEncoder


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


def jsonify(data: Any) -> JSON:
    """
    This function will encode and decode the data passed to it with DjangoJSONEncoder.

    This is useful, for example, to compare Python data and loaded JSON responses. A common use case is to compare
    serializer data with a response's JSON in a test case; comparing the serializer data directly may yield unexpected
    results, like UUID fields being considered different between the data and the response, even though they
    effectively represent the same UUID.
    """
    return cast(JSON, json.loads(json.dumps(data, cls=DjangoJSONEncoder)))


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
