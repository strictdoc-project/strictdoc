"""
@relation(REQ-1, scope=file)
"""
from typing import Optional


class SDocDocumentContext:
    def __init__(self) -> None:
        self.title_number_string: Optional[str] = None
