# core/extensions
This folder includes some useful "extensions" to Django itself, such as fields and widgets.


## Fields

### SVGField
A FileField specifically made for SVG images that will validate that the given image is an SVG file.


## Widgets

### ImagePreviewWidget
A FileInput widget that will display the current image bellow the file Input for a in-real-time preview.


## Admin

### UneditableFixedInline
A "fixed" version of Django's admin in-lines that does not display the title of the object in each line. Also prevents edition.
