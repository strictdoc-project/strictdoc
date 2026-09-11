from pathlib import Path

SUPPORTED_IMAGE_FORMATS: dict[str, str] = {
    ".svg": "image/svg+xml",
    ".png": "image/png",
    ".gif": "image/gif",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".webp": "image/webp",
    ".avif": "image/avif",
}

SUPPORTED_IMAGE_FORMAT_NAMES = "SVG, PNG, GIF, JPG, JPEG, WebP, AVIF"


def is_supported_image_format(filename: str, content_type: str | None) -> bool:
    extension = Path(filename).suffix.lower()
    expected_content_type = SUPPORTED_IMAGE_FORMATS.get(extension)
    return expected_content_type is not None and (
        content_type == expected_content_type
    )
