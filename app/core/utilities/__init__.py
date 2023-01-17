import xml.etree.cElementTree as et
from io import TextIOWrapper
from pathlib import Path
from typing import Optional
from uuid import uuid4
from django.core.files import File
from core.utilities.types import JSON_BASE


def empty(string: Optional[str]) -> bool:
    """Given a string, returns True if it's None or empty, or only whitespace."""
    if not string:
        return True
    if string.strip() == "":
        return True
    return False


def clear_json(json_obj: JSON_BASE) -> JSON_BASE:
    """Clear a JSON object before serializing by removing all 'None' values."""
    if isinstance(json_obj, dict):
        return {k: clear_json(v) for k, v in json_obj.items() if v is not None}
    if isinstance(json_obj, list):
        return [clear_json(v) for v in json_obj if v is not None]
    return json_obj


def ext(filename: str) -> str:
    """Given a filename, returns the extension."""
    return ".".join(filename.split(".")[1:])


def uuid() -> str:
    """Generate a random uuid4. This is a shorthand; equivalent to `str(uuid4())`."""
    return str(uuid4())


def is_svg(filepath: str | Path | File) -> bool:
    """
    Validate that a file is a valid SVG file.

    Taken and adjusted from: https://stackoverflow.com/questions/15136264/
    """

    def parse_file(f: TextIOWrapper | File) -> bool:
        tag = None
        try:
            for _, el in et.iterparse(f, ("start",)):
                tag = el.tag
                break
        except et.ParseError:
            pass
        return tag == "{http://www.w3.org/2000/svg}svg"

    if isinstance(filepath, File):
        return parse_file(filepath)
    else:
        with open(filepath, "r") as file:
            return parse_file(file)
