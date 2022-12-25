from typing import List

from strictdoc.backend.sdoc.models.node import Node
from strictdoc.helpers.auto_described import auto_described


@auto_described
class Fragment:  # pylint: disable=too-many-instance-attributes
    def __init__(  # pylint: disable=too-many-arguments
        self,
        section_contents: List[Node],
    ):
        self.section_contents = section_contents
        self.ng_level = None
        self.ng_has_requirements = False
