from typing import List

from strictdoc.backend.sdoc.models.object import SDocObject
from strictdoc.helpers.auto_described import auto_described


@auto_described
class Fragment:  # pylint: disable=too-many-instance-attributes
    def __init__(
        self,
        section_contents: List[SDocObject],
    ):
        self.section_contents = section_contents
        self.ng_level = None
        self.ng_has_requirements = False
