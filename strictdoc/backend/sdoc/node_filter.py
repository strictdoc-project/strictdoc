from strictdoc.backend.sdoc.models.model import (
    SDocElementIF,
)


class NodeFilter:
    def __init__(self, blacklisted_nodes: set[SDocElementIF]):
        self.blacklisted_nodes: set[SDocElementIF] = blacklisted_nodes

    def is_whitelisted(self, node: SDocElementIF) -> bool:
        return node not in self.blacklisted_nodes
