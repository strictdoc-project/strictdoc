"""
@relation(SDOC-SRS-34, scope=file)
"""

from typing import Any, Optional

from strictdoc.helpers.auto_described import auto_described


@auto_described
class Req:
    def __init__(self, parent: Any, uid: str):
        assert isinstance(uid, str)
        assert len(uid) > 0

        self.parent = parent
        self.uid: str = uid

        self.ng_source_line: Optional[int] = None
        self.ng_source_column: Optional[int] = None
