from typing import Optional

from strictdoc.backend.sdoc.models.document_grammar import GrammarElement
from strictdoc.backend.sdoc.models.requirement import Requirement
from strictdoc.backend.sdoc.models.section import Section
from strictdoc.core.traceability_index import TraceabilityIndex
from strictdoc.helpers.cast import assert_cast


class QueryObject:
    def __init__(self, traceability_index: TraceabilityIndex):
        self.traceability_index: TraceabilityIndex = traceability_index
        self.current_node = None

    @property
    def is_requirement(self):
        return self.current_node.is_requirement

    @property
    def is_section(self):
        return self.current_node.is_section

    @property
    def is_root(self):
        return self.current_node.is_root

    @property
    def has_parent_requirements(self):
        return self.traceability_index.has_parent_requirements(
            self.current_node
        )

    def __getitem__(self, field_name: str) -> Optional[str]:
        if self.current_node.is_requirement:
            requirement: Requirement = assert_cast(
                self.current_node, Requirement
            )
            element: GrammarElement = (
                requirement.document.grammar.elements_by_type[
                    requirement.requirement_type
                ]
            )
            grammar_field_titles = list(map(lambda f: f.title, element.fields))
            if field_name not in grammar_field_titles:
                raise AttributeError(f"No such requirement field: {field_name}")
            field_value = requirement._get_cached_field(
                field_name, singleline_only=True
            )
            if field_value is not None:
                return field_value
            return None
        elif self.current_node.is_section:
            section: Section = assert_cast(self.current_node, Section)
            if field_name == "UID":
                return section.reserved_uid
            elif field_name == "TITLE":
                return section.title
            raise AttributeError(f"No such section field: {field_name}")
        else:
            raise NotImplementedError
