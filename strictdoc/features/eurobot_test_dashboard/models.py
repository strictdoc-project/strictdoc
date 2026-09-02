"""
Plain data holders for the Eurobot test dashboard: one gap item per
affected node, one coverage gap per check, one dashboard scope per
revision-filter value.

@relation(SDOC-SRS-97, scope=file)
"""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class GapItem:
    uid: str
    title: str
    url: str
    # Only gap 4 (tests not yet passed) sets this, to show the current
    # STATUS value next to the test case.
    status: Optional[str] = None


@dataclass
class CoverageGap:
    name: str
    items: List[GapItem] = field(default_factory=list)

    @property
    def count(self) -> int:
        return len(self.items)


@dataclass
class DashboardScope:
    """
    One revision-filter value's own set of four gaps: "all" (no filter),
    "<revision> only", or "up to and including <revision>".
    """

    key: str
    label: str
    gaps: List[CoverageGap]
