# core/extensions
This folder includes some useful "extensions" to Django itself, such as fields and widgets. Also includes an `utils.py` file with useful, common functions.


## Fields

### SVGField
A FileField specifically made for SVG images that will validate that the given image is an SVG file.


## Widgets

### ImagePreviewWidget
A FileInput widget that will display the current image bellow the file Input for a in-real-time preview.
