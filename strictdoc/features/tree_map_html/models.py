"""
Data contract between Python tree map definitions and the browser renderer.

@relation(SDOC-SRS-157, scope=file)
"""

from dataclasses import dataclass
from typing import Tuple

import orjson


@dataclass(frozen=True)
class TreeMapNode:
    label: str
    weight: int
    color: str
    children: Tuple["TreeMapNode", ...]


@dataclass(frozen=True)
class TreeMap:
    title: str
    root: TreeMapNode


@dataclass(frozen=True)
class TreeMapData:
    tree_maps: Tuple[TreeMap, ...]

    def to_json(self) -> str:
        return orjson.dumps(self).decode("utf-8")
