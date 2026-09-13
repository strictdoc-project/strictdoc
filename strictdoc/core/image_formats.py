"""
Image formats supported by StrictDoc's drag-and-drop/paste image upload and
by the wildcard-based RST/Sphinx image directive
(strictdoc/backend/rst/directives/wildcard_enhanced_image.py). This is the
single source of truth for the supported extensions and their expected MIME
content types; the client-side upload script
(strictdoc/export/html/_static/editable_field.js) mirrors this list for
same-format checks in the browser.
"""

from enum import Enum
from pathlib import Path


class ImageFormat(Enum):
    SVG = (".svg", "image/svg+xml")
    PNG = (".png", "image/png")
    GIF = (".gif", "image/gif")
    JPG = (".jpg", "image/jpeg")
    JPEG = (".jpeg", "image/jpeg")
    WebP = (".webp", "image/webp")
    AVIF = (".avif", "image/avif")

    def __init__(self, extension: str, content_type: str) -> None:
        self.extension = extension
        self.content_type = content_type

    @classmethod
    def names(cls) -> str:
        return ", ".join(image_format.name for image_format in cls)


SUPPORTED_IMAGE_FORMATS: dict[str, str] = {
    image_format.extension: image_format.content_type
    for image_format in ImageFormat
}

SUPPORTED_IMAGE_FORMAT_NAMES = ImageFormat.names()


def is_supported_image_format(filename: str, content_type: str | None) -> bool:
    extension = Path(filename).suffix.lower()
    expected_content_type = SUPPORTED_IMAGE_FORMATS.get(extension)
    return expected_content_type is not None and (
        content_type == expected_content_type
    )
