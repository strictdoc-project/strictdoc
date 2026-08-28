import os
from pathlib import Path

import pytest

from strictdoc.commands.manage_assets_command import ManageAssetsCommand


def test_cleanup_continues_after_deletion_error(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    first_asset = tmp_path / "first.svg"
    failed_asset = tmp_path / "failed.svg"
    last_asset = tmp_path / "last.svg"
    for asset in (first_asset, failed_asset, last_asset):
        asset.write_text("<svg/>", encoding="utf8")

    original_remove = os.remove

    def remove_with_one_failure(path: Path) -> None:
        if Path(path) == failed_asset:
            raise PermissionError("permission denied")
        original_remove(path)

    monkeypatch.setattr("os.remove", remove_with_one_failure)
    command = ManageAssetsCommand.__new__(ManageAssetsCommand)

    command._delete_unused_assets(
        [str(first_asset), str(failed_asset), str(last_asset)]
    )

    assert not first_asset.exists()
    assert failed_asset.exists()
    assert not last_asset.exists()
    output = capsys.readouterr().out
    assert (
        f"Could not delete {failed_asset.as_posix()}: permission denied"
        in output
    )
    assert "Cleanup complete: 2 deleted, 1 failed." in output
