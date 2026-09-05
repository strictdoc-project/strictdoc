"""
Data contract between Python tree map definitions and the browser renderer.

@relation(SDOC-SRS-157, scope=file)
"""

from dataclasses import dataclass
from typing import Optional, Tuple

import orjson


@dataclass(frozen=True)
class TreeMapNode:
    identifier: str
    label: str
    count: Optional[int]
    weight: int
    color: Optional[str]
    children: Tuple["TreeMapNode", ...]
    title: Optional[str] = None
    mid: Optional[str] = None
    uid: Optional[str] = None
    document_url: Optional[str] = None
    preview_url: Optional[str] = None


@dataclass(frozen=True)
class TreeMapLegendItem:
    color: str
    text: str


@dataclass(frozen=True)
class TreeMap:
    identifier: str
    title: str
    description: str
    legend: Tuple[TreeMapLegendItem, ...]
    root: TreeMapNode


@dataclass(frozen=True)
class TreeMapData:
    tree_maps: Tuple[TreeMap, ...]

    def to_json(self) -> str:
        return orjson.dumps(self).decode("utf-8")
