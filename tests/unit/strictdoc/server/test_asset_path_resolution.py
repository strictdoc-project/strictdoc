import os

import pytest

from strictdoc.server.routers.main_router import (
    resolve_path_in_output_root,
    resolve_uploaded_asset_subfolder,
)


@pytest.mark.parametrize(
    (
        "mids_enabled",
        "requirement_exists",
        "requirement_mid_permanent",
        "requirement_uid",
        "expected_subfolder",
    ),
    [
        (True, False, False, None, "a" * 32),
        (False, True, True, None, "a" * 32),
        (False, True, False, "REQ 1/2", "REQ_1_2"),
        (False, True, False, None, ""),
        (False, False, False, None, None),
    ],
)
def test_resolve_uploaded_asset_subfolder(
    mids_enabled: bool,
    requirement_exists: bool,
    requirement_mid_permanent: bool,
    requirement_uid: str | None,
    expected_subfolder: str | None,
) -> None:
    assert (
        resolve_uploaded_asset_subfolder(
            mids_enabled=mids_enabled,
            requirement_mid="a" * 32,
            requirement_exists=requirement_exists,
            requirement_mid_permanent=requirement_mid_permanent,
            requirement_uid=requirement_uid,
        )
        == expected_subfolder
    )


@pytest.mark.parametrize(
    "url_path",
    [
        "_static/base.css",
        "_static/fonts/../base.css",
    ],
)
def test_resolve_path_in_output_root_inside_output_root(tmp_path, url_path):
    output_root = tmp_path / "html"

    assert resolve_path_in_output_root(
        str(output_root), url_path
    ) == os.path.join(os.path.realpath(output_root), "_static", "base.css")


@pytest.mark.parametrize(
    "url_path",
    [
        "../secret.txt",
        "_static/../../secret.txt",
        "../html_other/secret.txt",
        "../secret.html",
    ],
)
def test_resolve_path_in_output_root_outside_output_root(tmp_path, url_path):
    output_root = tmp_path / "html"

    assert resolve_path_in_output_root(str(output_root), url_path) is None


def test_resolve_path_in_output_root_absolute_path(tmp_path):
    output_root = tmp_path / "html"
    secret_file = tmp_path / "secret.txt"

    assert (
        resolve_path_in_output_root(str(output_root), str(secret_file)) is None
    )
