from dataclasses import dataclass, field
from typing import Dict, List

from spdx_tools.spdx3.model import (
    Element,
    Relationship,
    SpdxDocument,
)
from spdx_tools.spdx3.model.software import File, Package, Snippet


@dataclass
class SPDXSDocContainer:
    document: SpdxDocument = None
    package: Package = None
    files: List[File] = field(default_factory=list)
    snippets: List[Snippet] = field(default_factory=list)
    relationships: List[Relationship] = field(default_factory=list)
    map_spdx_ref_to_objects: Dict[str, Element] = field(default_factory=dict)
    map_spdx_snippets_to_files: Dict[str, str] = field(default_factory=dict)
