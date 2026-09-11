import pytest

from strictdoc.core.image_formats import is_supported_image_format


@pytest.mark.parametrize(
    ("filename", "content_type"),
    [
        ("picture.svg", "image/svg+xml"),
        ("picture.png", "image/png"),
        ("picture.gif", "image/gif"),
        ("picture.jpg", "image/jpeg"),
        ("picture.jpeg", "image/jpeg"),
        ("picture.webp", "image/webp"),
        ("picture.avif", "image/avif"),
    ],
)
def test_supported_image_format(filename: str, content_type: str) -> None:
    assert is_supported_image_format(filename, content_type)


@pytest.mark.parametrize(
    ("filename", "content_type"),
    [
        ("picture.tiff", "image/tiff"),
        ("document.pdf", "application/pdf"),
        ("picture.webp", "application/octet-stream"),
        ("picture.avif", "image/webp"),
        ("picture", "image/png"),
    ],
)
def test_unsupported_image_format(filename: str, content_type: str) -> None:
    assert not is_supported_image_format(filename, content_type)
