from enum import IntEnum


class GraphLinkType(IntEnum):
    MID_TO_NODE = 1
    UID_TO_NODE = 2
    NODE_TO_PARENT_NODES = 3
    NODE_TO_CHILD_NODES = 4
    NODE_TO_INCOMING_LINKS = 5
    DOCUMENT_TO_TAGS = 8
