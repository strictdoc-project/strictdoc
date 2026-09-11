import pytest

from strictdoc.server.routers.main_router import (
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
