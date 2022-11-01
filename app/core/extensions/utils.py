from io import TextIOWrapper
from pathlib import Path
import xml.etree.cElementTree as et
from django.core.files import File


def ext(filename: str) -> str:
    """Given a filename, returns the extension."""
    return ".".join(filename.split(".")[1:])


def is_svg(filepath: str | Path | File) -> bool:
    """
    Validate that a file is a valid SVG file.

    Taken and adjusted from: https://stackoverflow.com/questions/15136264/
    """
    def parse_file(f: TextIOWrapper | File) -> bool:
        tag = None
        try:
            for _, el in et.iterparse(f, ('start',)):
                tag = el.tag
                break
        except et.ParseError:
            pass
        return tag == '{http://www.w3.org/2000/svg}svg'
    if isinstance(filepath, File):
        return parse_file(filepath)
    else:
        with open(filepath, "r") as file:
            return parse_file(file)
