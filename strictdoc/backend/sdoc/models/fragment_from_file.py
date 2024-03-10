from typing import List, Optional

from strictdoc.backend.sdoc.models.fragment import Fragment
from strictdoc.helpers.auto_described import auto_described


@auto_described
class FragmentFromFile:
    def __init__(
        self,
        parent,
        file,
    ):
        self.parent = parent
        self.file = file

        self.ng_level = None
        self.ng_has_requirements = False
        self.resolved_fragment: Optional[Fragment] = None

    @property
    def document(self):
        raise NotImplementedError

    def has_any_requirements(self) -> bool:
        task_list = list(self.section_contents)
        while len(task_list) > 0:
            section_or_requirement = task_list.pop(0)
            if isinstance(section_or_requirement, FragmentFromFile):
                if section_or_requirement.has_any_requirements():
                    return True
            if section_or_requirement.is_requirement:
                return True
            assert section_or_requirement.is_section, section_or_requirement
            task_list.extend(section_or_requirement.section_contents)
        return False

    @property
    def section_contents(self) -> List:
        assert self.resolved_fragment is not None, self.resolved_fragment
        return self.resolved_fragment.section_contents
