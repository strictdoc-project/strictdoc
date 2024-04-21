# mypy: disable-error-code="arg-type"
from dataclasses import dataclass, field
from typing import List, Optional

from strictdoc.backend.sdoc.models.node import SDocNode


@dataclass
class DocumentStats:
    requirements_total: int = 0
    requirements_no_uid: List[SDocNode] = field(default_factory=list)


@dataclass
class DocumentTreeStats:  # pylint: disable=too-many-instance-attributes
    total_documents: int = 0
    total_requirements: int = 0
    total_sections: int = 0
    total_tbd: int = 0
    total_tbc: int = 0
    git_commit_hash: Optional[str] = None

    # Section
    sections_without_free_text: int = 0

    # UID
    requirements_no_uid: int = 0
    requirements_no_links: int = 0
    requirements_root_no_links: int = 0
    requirements_no_rationale: int = 0

    # STATUS
    requirements_status_none: int = 0
    requirements_status_draft: int = 0
    requirements_status_backlog: int = 0
    requirements_status_active: int = 0
    requirements_status_other: int = 0

    # Document-level stats.
    document_level_stats: List[DocumentStats] = field(
        default_factory=DocumentStats
    )
