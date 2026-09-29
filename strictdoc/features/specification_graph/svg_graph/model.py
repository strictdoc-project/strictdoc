"""
Input model of the graph generator.

The model does not depend on the StrictDoc document model. An adapter
converts StrictDoc data into this model.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional, Tuple


class LayoutMode(Enum):
    LEVELS = "levels"
    LEVELS_WITH_GROUPS = "levels_with_groups"
    STRUCTURE = "structure"


@dataclass(frozen=True)
class GraphNode:
    node_id: str
    title: str
    link: Optional[str] = None
    details: Tuple[Tuple[str, str], ...] = ()
    children: Tuple["GraphNode", ...] = ()
    group_id: Optional[str] = None


@dataclass(frozen=True)
class GraphGroup:
    group_id: str
    title: str


@dataclass(frozen=True)
class GraphEdge:
    source_id: str
    target_id: str
    relation_type: str


@dataclass(frozen=True)
class Graph:
    mode: LayoutMode
    root: Tuple[GraphNode, ...]
    edges: Tuple[GraphEdge, ...] = ()
    groups: Tuple[GraphGroup, ...] = ()
