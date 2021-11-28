from typing import List

from strictdoc.imports.reqif.stage1.models.reqif_spec_hierarchy import (
    ReqIFSpecHierarchy,
)


class ReqIFSpecification:
    def __init__(
        self,
        identifier: str,
        long_name: str,
        children: List[ReqIFSpecHierarchy],
    ):
        self.identifier: str = identifier
        self.long_name: str = long_name
        self.children: List[ReqIFSpecHierarchy] = children

    def __repr__(self):
        return (
            f"ReqIFSpecification("
            f"identifier: {self.identifier},"
            f"children: {self.children},"
            f")"
        )
