from typing import Any
from django.core.exceptions import ValidationError
from django.core.files import File
from django.db import models
from core.utilities import is_svg


class SVGField(models.FileField):
    """FileField for SVG images that validates the file given."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        validators = kwargs.get("validators", [])
        validators.append(SVGField.svg_validator)
        kwargs["validators"] = validators
        super().__init__(*args, **kwargs)

    @staticmethod
    def svg_validator(file: File) -> None:
        if not is_svg(file):
            raise ValidationError("File is not an SVG!")
