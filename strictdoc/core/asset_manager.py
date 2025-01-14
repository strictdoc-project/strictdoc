# mypy: disable-error-code="no-untyped-def"
from dataclasses import dataclass
from typing import Dict, List

from strictdoc.helpers.paths import SDocRelativePath


@dataclass
class AssetDir:
    full_path: str
    relative_path: SDocRelativePath

    def __post_init__(self):
        assert isinstance(self.relative_path, SDocRelativePath), (
            self.relative_path
        )


class AssetManager:
    def __init__(self) -> None:
        self.asset_dirs: List[AssetDir] = []
        self.asset_dirs_lookup: Dict[SDocRelativePath, AssetDir] = {}

    def add_asset_dir(self, full_path: str, relative_path: SDocRelativePath):
        asset_dir = AssetDir(full_path=full_path, relative_path=relative_path)
        self.asset_dirs.append(asset_dir)

        self.asset_dirs_lookup[relative_path] = asset_dir

    def iterate(self):
        yield from self.asset_dirs
