from collections import OrderedDict
from dataclasses import dataclass
from typing import Dict, List, Optional, Set, Tuple

from strictdoc.backend.sdoc.models.document import SDocDocument
from strictdoc.backend.sdoc.models.document_grammar import (
    GrammarElement,
)
from strictdoc.backend.sdoc.models.node import SDocNode, SDocNodeField
from strictdoc.backend.sdoc.models.type_system import GrammarElementField
from strictdoc.core.traceability_index import (
    TraceabilityIndex,
)
from strictdoc.export.html.form_objects.document_grammar_form_object import (
    GrammarElementFormObject,
)
from strictdoc.helpers.cast import assert_cast


@dataclass
class UpdateRequirementResult:
    this_document_requirements_to_update: Set[SDocNode]


class UpdateGrammarElementCommand:
    def __init__(
        self,
        *,
        form_object: GrammarElementFormObject,
        document: SDocDocument,
        traceability_index: TraceabilityIndex,
    ):
        self.form_object: GrammarElementFormObject = form_object
        self.document: SDocDocument = document
        self.traceability_index: TraceabilityIndex = traceability_index

    def perform(self) -> bool:
        form_object: GrammarElementFormObject = self.form_object
        document: SDocDocument = self.document
        existing_element: GrammarElement = document.grammar.get_element_by_mid(
            form_object.element_mid
        )

        grammar_fields: Dict[str, GrammarElementField] = {}
        for grammar_field in existing_element.fields:
            grammar_fields[grammar_field.mid] = grammar_field

        # Prepare fields that could have been renamed by the user has just saved the form.
        renamed_fields_lookup = {}
        for field in form_object.fields:
            if field.field_mid not in grammar_fields:
                continue
            existing_field = grammar_fields[field.field_mid]
            if field.field_name != existing_field.title:
                renamed_fields_lookup[field.field_name] = existing_field.title

        """
        Convert the form object to an updated grammar element.
        """
        updated_element: GrammarElement = (
            form_object.convert_to_grammar_element(document.grammar)
        )

        """
        Compare if anything was changed in the new grammar.
        """
        document_grammar_field_names = updated_element.get_field_titles()

        existing_document_grammar_field_names = (
            existing_element.get_field_titles()
        )
        grammar_changed = (
            document_grammar_field_names
            != existing_document_grammar_field_names
        )
        existing_requirement_element = document.grammar.elements_by_type[
            existing_element.tag
        ]
        grammar_changed = (
            grammar_changed
            or existing_requirement_element.relations
            != updated_element.relations
        )
        if not grammar_changed:
            return False

        document.grammar.update_element(existing_element, updated_element)

        document_iterator = self.traceability_index.document_iterators[document]

        for node in document_iterator.all_content():
            if not node.is_requirement:
                continue

            requirement: SDocNode = assert_cast(node, SDocNode)
            if requirement.requirement_type != updated_element.tag:
                continue

            requirement_field_names = list(
                requirement.ordered_fields_lookup.keys()
            )

            # Rewrite requirement fields because some fields could have been
            # renamed.
            new_ordered_fields_lookup: OrderedDict[str, List[SDocNodeField]] = (
                OrderedDict()
            )

            for document_grammar_field_name in document_grammar_field_names:
                # We need to find a previous field name in case the field was
                # renamed.
                previous_field_name = renamed_fields_lookup.get(
                    document_grammar_field_name, document_grammar_field_name
                )

                # If the field does not exist in the grammar fields anymore,
                # delete the requirement field.
                if previous_field_name not in requirement_field_names:
                    continue

                previous_fields: List[SDocNodeField] = (
                    requirement.ordered_fields_lookup[previous_field_name]
                )
                for previous_field in previous_fields:
                    previous_field.field_name = document_grammar_field_name

                new_ordered_fields_lookup[document_grammar_field_name] = (
                    previous_fields
                )

            registered_relation_types: Set[Tuple[str, Optional[str]]] = set()
            for relation in existing_requirement_element.relations:
                registered_relation_types.add(
                    (relation.relation_type, relation.relation_role)
                )
            if "REFS" in requirement.ordered_fields_lookup:
                existing_refs_field = requirement.ordered_fields_lookup["REFS"][
                    0
                ]
                new_relations = []
                for (
                    requirement_relation_
                ) in existing_refs_field.field_value_references:
                    if (
                        requirement_relation_.ref_type,
                        requirement_relation_.role,
                    ) in registered_relation_types:
                        new_relations.append(requirement_relation_)
                new_ordered_fields_lookup["REFS"] = [existing_refs_field]
            requirement.ordered_fields_lookup = new_ordered_fields_lookup
            requirement.ng_reserved_fields_cache.clear()

        return True
