"""
Input model of the graph generator.

The model does not depend on the StrictDoc document model. An adapter
converts StrictDoc data into this model.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Mapping, Optional, Tuple


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
class RelationStyle:
    """
    Style of a relation type.

    A relation has one type. A type has one style.
    """

    label: str
    color: str
    # Value of the SVG stroke-dasharray. None draws a solid line.
    dash: Optional[str] = None


# Built-in relation types. spec.md, section "Типы связей и стили", defines
# the situations in which the generator assigns them.
DEFAULT_RELATION_TYPE = "default"
SECONDARY_RELATION_TYPE = "secondary"
WARNING_RELATION_TYPE = "warning"
DANGER_RELATION_TYPE = "danger"

BUILTIN_RELATION_STYLES: Dict[str, RelationStyle] = {
    DEFAULT_RELATION_TYPE: RelationStyle(label="Relation", color="#222222"),
    SECONDARY_RELATION_TYPE: RelationStyle(
        label="Secondary relation", color="#8a8a8a"
    ),
    WARNING_RELATION_TYPE: RelationStyle(
        label="Warning", color="#222222", dash="6 4"
    ),
    DANGER_RELATION_TYPE: RelationStyle(label="Danger", color="#c00000"),
}


@dataclass(frozen=True)
class Graph:
    mode: LayoutMode
    root: Tuple[GraphNode, ...]
    edges: Tuple[GraphEdge, ...] = ()
    groups: Tuple[GraphGroup, ...] = ()
    # Styles of the relation types. An entry for a built-in type replaces
    # its default style.
    relation_types: Mapping[str, RelationStyle] = field(default_factory=dict)
