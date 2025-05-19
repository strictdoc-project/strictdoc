import typing
from collections import Counter
from dataclasses import dataclass, field
from typing import Dict, List

from strictdoc.backend.sdoc.models.document import SDocDocument
from strictdoc.backend.sdoc.models.node import SDocNode
from strictdoc.backend.sdoc.models.section import SDocSection
from strictdoc.helpers.string import create_safe_title_string


@dataclass
class SinglePrefixRequirements:
    requirements_uid_numbers: List[int] = field(default_factory=list)
    requirements_no_uid: List[SDocNode] = field(default_factory=list)


@dataclass
class DocumentStats:
    document: SDocDocument
    requirements_per_prefix: Dict[str, SinglePrefixRequirements] = field(
        default_factory=dict
    )
    sections_without_uid: List[typing.Union[SDocNode, SDocSection]] = field(
        default_factory=list
    )
    section_uids_so_far: typing.Counter[str] = field(default_factory=Counter)


@dataclass
class DocumentTreeStats:
    single_document_stats: List[DocumentStats]

    requirements_per_prefix: Dict[str, SinglePrefixRequirements]
    section_uids_so_far: typing.Counter[str]

    def get_next_requirement_uid(self, prefix: str) -> str:
        next_number = self.get_next_requirement_uid_number(prefix)
        return f"{prefix}{next_number}"

    def get_next_requirement_uid_number(self, prefix: str) -> int:
        if prefix not in self.requirements_per_prefix:
            return 1

        single_prefix_requirements = self.requirements_per_prefix[prefix]

        one_prefix_requirements_uid_numbers = (
            single_prefix_requirements.requirements_uid_numbers
        )
        next_number = (
            max(one_prefix_requirements_uid_numbers) + 1
            if len(one_prefix_requirements_uid_numbers) > 0
            else 1
        )
        return next_number

    def get_auto_section_uid(
        self,
        document_acronym: str,
        section: typing.Union[SDocNode, SDocSection],
    ) -> str:
        if section.reserved_title is None:
            return ""

        section_title = create_safe_title_string(section.reserved_title)
        auto_uid = f"SECTION-{document_acronym}-{section_title}"

        count_so_far = self.section_uids_so_far[auto_uid]
        self.section_uids_so_far[auto_uid] += 1

        if count_so_far >= 1:
            auto_uid += f"-{self.section_uids_so_far[auto_uid]}"
        return auto_uid
