from typing import List

from strictdoc.backend.sdoc.models.node import Node


class Fragment:  # pylint: disable=too-many-instance-attributes
    def __init__(  # pylint: disable=too-many-arguments
        self,
        section_contents: List[Node],
    ):
        self.section_contents = section_contents
        self.ng_level = None
        self.ng_has_requirements = False

    def __str__(self):
        return (
            f"Fragment("
            f"id: {id(self)}, "
            f"section_contents: {self.section_contents})"
        )

    def __repr__(self):
        return self.__str__()
