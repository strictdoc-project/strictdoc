from strictdoc.backend.sdoc.models.node import Node
from strictdoc.backend.sdoc.models.section import SectionContext


class FragmentFromFile(Node):  # pylint: disable=too-many-instance-attributes
    def __init__(  # pylint: disable=too-many-arguments
        self,
        parent,
        file,
    ):
        self.parent = parent
        self.file = file

        self.ng_level = None
        self.ng_has_requirements = False
        self.ng_document_reference = None
        self.context = SectionContext()

    def __str__(self):
        return f"FragmentFromFile(level: {self.ng_level}, file: {self.file})"

    def __repr__(self):
        return self.__str__()

    @property
    def document(self):
        return self.ng_document_reference.get_document()

    @property
    def is_requirement(self):
        return False

    @property
    def is_composite_requirement(self):
        return False

    @property
    def is_section(self):
        return True
