"""
@relation(SDOC-SRS-33, scope=file)
"""

from enum import Enum

REGEX_REQ = r"(?!scope=)[A-Za-z][A-Za-z0-9_\/\.\\-]+"
REGEX_ROLE = r"[A-Za-z][A-Za-z0-9\\-]+"
RESERVED_KEYWORDS = "FIXME|NOTE|TODO|TBD|WARNING"


class FunctionAttribute(Enum):
    STATIC = "static"
    DECLARATION = "declaration"
    DEFINITION = "definition"
