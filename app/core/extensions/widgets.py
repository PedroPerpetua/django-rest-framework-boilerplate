from typing import Any
from django.forms.widgets import FileInput
from django.utils.safestring import mark_safe, SafeText


class ImagePreviewWidget(FileInput):
    """Widget to display the current image bellow the file input."""

    def __init__(
        self,
        original_src: str,
        min_size: int | str=150,
        max_size: int | str=500,
        error_string: str="Error! Image cannot be displayed!",
        *args: Any,
        **kwargs: Any
    ):
        super().__init__(*args, **kwargs)
        self.original_src = original_src # src to display on error
        if isinstance(min_size, int):
            min_size = f"{min_size}px"
        self.min_size = min_size
        if isinstance(max_size, int):
            max_size = f"{max_size}px"
        self.max_size = max_size
        self.error_string = error_string

    def render(
        self, name: str, value: Any, *args: Any, **kwargs: Any
    ) -> SafeText:
        input_html = super().render(name, value, *args, **kwargs)
        # Make sure we have all the data we need
        if not hasattr(value, "url"):
            # No value found... let's use the default
            # This happens, for example, if the form has validation errors.
            value.url = self.original_src
        input_id = kwargs["attrs"]["id"]
        img_id = f"{input_id}_IMG"
        # Render the HTML for the widget.
        return mark_safe(f"""
            <div>
              {input_html} <br />
              <img id="{img_id}" src="{value.url}" alt="{self.error_string}"/>
            </div>"""
            # Write a script to change the image on input change
            f"""
            <script>
              const imageContainer = document.querySelector("#{img_id}");
              const originalImage = imageContainer.src;

              document.querySelector("#{input_id}").addEventListener(
                "change", (event) => {{
                  const input = event.target;
                  if (!(input.files && input.files[0])) {{
                    imageContainer.src = originalImage;
                    return;
                  }}
                  const reader = new FileReader();
                  reader.onload = (e) => {{
                    imageContainer.src = e.target.result;
                  }}
                  reader.readAsDataURL(input.files[0]);
                }}
              );
            </script>
        """
        # Setup some styling
        f"""
        <style>
        #{img_id} {{
            margin-top: 10px;
            max-width: {self.max_size};
            max-height: {self.max_size};
            min-width: {self.min_size};
            min-height: {self.min_size};
        }}
        </style>
        """)
