"""
@relation(SDOC-SRS-141, scope=file)
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Union

from strictdoc.backend.sdoc_source_code.models.function_range_marker import (
    FunctionRangeMarker,
)
from strictdoc.backend.sdoc_source_code.models.line_marker import LineMarker
from strictdoc.backend.sdoc_source_code.models.range_marker import (
    RangeMarker,
)


@dataclass
class SourceNode:
    entity_name: Optional[str]
    markers: List[Union[FunctionRangeMarker, RangeMarker, LineMarker]] = field(
        default_factory=list
    )
    fields: Dict[str, str] = field(default_factory=dict)
