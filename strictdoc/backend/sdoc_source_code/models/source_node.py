"""
@relation(SDOC-SRS-141, scope=file)
"""

from dataclasses import dataclass, field
from typing import Any, List, Optional, Union

from strictdoc.backend.sdoc_source_code.models.function import Function
from strictdoc.backend.sdoc_source_code.models.function_range_marker import (
    FunctionRangeMarker,
)
from strictdoc.backend.sdoc_source_code.models.line_marker import LineMarker
from strictdoc.backend.sdoc_source_code.models.range_marker import (
    RangeMarker,
)
from strictdoc.backend.sdoc_source_code.models.source_location import ByteRange
from strictdoc.core.project_config import SourceNodesEntry


@dataclass(eq=False)
class SourceNode:
    """
    NOTE: eq=False is needed to make this dataclass support being a dictionary key.

    eq=False means that dictionaries will index by object identity. Copied
    SourceNode objects will appear as two different SourceNodes. An alternative
    could be to implement __eq__ and __hash__ so that they target byte_range.
    """

    entity_name: Optional[str]
    comment_byte_range: Optional[ByteRange]
    markers: List[Union[FunctionRangeMarker, RangeMarker, LineMarker]] = field(
        default_factory=list
    )
    fields: dict[str, str] = field(default_factory=dict)
    fields_locations: dict[str, tuple[int, int]] = field(default_factory=dict)
    function: Optional[Function] = None
    # FIXME: Adding SDocNode here causes circular import problem.
    sdoc_node: Optional[Any] = None

    def get_sdoc_field(
        self,
        field_name: str,
        cfg_entry: SourceNodesEntry,
    ) -> Optional[str]:
        if field_name in cfg_entry.sdoc_to_source_map:
            field_name = cfg_entry.sdoc_to_source_map[field_name]
        return self.fields.get(field_name)

    def get_sdoc_fields(self, cfg_entry: SourceNodesEntry) -> dict[str, str]:
        """
        Get SDoc representation of all available fields.

        Returns a dict equivalent to self.fields unless config option 'sdoc_to_source_map' is set.
        """
        fields = {
            field_name: self.fields[field_name]
            for field_name in self.fields
            if field_name not in cfg_entry.sdoc_to_source_map.values()
        }
        for (
            field_name,
            mapped_field_name,
        ) in cfg_entry.sdoc_to_source_map.items():
            if mapped_field_name in self.fields:
                fields[field_name] = self.fields[mapped_field_name]
        return fields
