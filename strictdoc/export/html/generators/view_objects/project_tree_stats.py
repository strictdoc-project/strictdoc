from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from strictdoc.backend.sdoc.models.node import SDocNode


@dataclass
class DocumentStats:
    requirements_total: int = 0
    requirements_no_uid: List[SDocNode] = field(default_factory=list)


@dataclass
class DocumentTreeStats:
    total_documents: int = 0
    total_requirements: int = 0
    total_sections: int = 0
    total_tbd: int = 0
    total_tbc: int = 0
    git_commit_hash: Optional[str] = None

    # Section.
    sections_without_text_nodes: int = 0

    # UID.
    requirements_no_uid: int = 0
    requirements_no_links: int = 0
    requirements_root_no_links: int = 0
    requirements_no_rationale: int = 0

    # STATUS.
    requirements_status_breakdown: Dict[Optional[str], int] = field(
        default_factory=lambda: defaultdict(int)
    )

    def sort_requirements_status_breakdown(self) -> None:
        self.requirements_status_breakdown = dict(
            sorted(
                self.requirements_status_breakdown.items(),
                key=lambda item: (item[0] is not None, item[1]),
                reverse=True,
            )
        )
