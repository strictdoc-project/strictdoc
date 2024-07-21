from typing import Union

from strictdoc.backend.sdoc.models.document import SDocDocument
from strictdoc.backend.sdoc.models.node import SDocCompositeNode, SDocNode
from strictdoc.backend.sdoc.models.section import SDocSection

SDocAnyNode = Union[
    SDocCompositeNode,
    SDocSection,
    SDocNode,
    SDocDocument,
]
