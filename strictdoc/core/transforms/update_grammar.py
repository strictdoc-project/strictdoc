from collections import OrderedDict
from dataclasses import dataclass
from typing import Dict, List, Optional, Set, Tuple

from strictdoc.backend.sdoc.models.document import Document
from strictdoc.backend.sdoc.models.document_grammar import DocumentGrammar
from strictdoc.backend.sdoc.models.requirement import (
    Requirement,
    RequirementField,
)
from strictdoc.backend.sdoc.models.type_system import GrammarElementField
from strictdoc.core.traceability_index import (
    TraceabilityIndex,
)
from strictdoc.export.html.form_objects.document_grammar_form_object import (
    DocumentGrammarFormObject,
)
from strictdoc.helpers.cast import assert_cast


@dataclass
class UpdateRequirementResult:
    this_document_requirements_to_update: Set[Requirement]


class UpdateGrammarCommand:
    def __init__(
        self,
        *,
        form_object: DocumentGrammarFormObject,
        document: Document,
        traceability_index: TraceabilityIndex,
    ):
        self.form_object: DocumentGrammarFormObject = form_object
        self.document: Document = document
        self.traceability_index: TraceabilityIndex = traceability_index

    def perform(self) -> bool:
        form_object: DocumentGrammarFormObject = self.form_object
        document: Document = self.document

        grammar_fields: Dict[str, GrammarElementField] = {}
        for grammar_field in document.grammar.elements[0].fields:
            grammar_fields[grammar_field.mid] = grammar_field

        # Prepare fields that could have been renamed by the user has just saved the form.
        renamed_fields_lookup = {}
        for field in form_object.fields:
            if field.field_mid not in grammar_fields:
                continue
            existing_field = grammar_fields[field.field_mid]
            if field.field_name != existing_field.title:
                renamed_fields_lookup[field.field_name] = existing_field.title

        # Create new grammar.
        document_grammar: DocumentGrammar = (
            form_object.convert_to_document_grammar()
        )

        # Compare if anything was changed in the new grammar.
        document_grammar_field_names = document_grammar.fields_order_by_type[
            "REQUIREMENT"
        ]
        existing_document_grammar_field_names = (
            document.grammar.fields_order_by_type["REQUIREMENT"]
        )
        grammar_changed = (
            document_grammar_field_names
            != existing_document_grammar_field_names
        )
        existing_requirement_element = document.grammar.elements_by_type[
            "REQUIREMENT"
        ]
        new_requirement_element = document_grammar.elements_by_type[
            "REQUIREMENT"
        ]
        grammar_changed = (
            grammar_changed
            or existing_requirement_element.relations
            != new_requirement_element.relations
        )
        if not grammar_changed:
            return False

        document_grammar.parent = document
        document.grammar = document_grammar

        document_iterator = self.traceability_index.document_iterators[document]

        for node in document_iterator.all_content():
            if not node.is_requirement:
                continue

            requirement: Requirement = assert_cast(node, Requirement)
            requirement_field_names = list(
                requirement.ordered_fields_lookup.keys()
            )

            # Rewrite requirement fields because some fields could have been
            # renamed.
            new_ordered_fields_lookup: OrderedDict[
                str, List[RequirementField]
            ] = OrderedDict()

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

                previous_fields: List[
                    RequirementField
                ] = requirement.ordered_fields_lookup[previous_field_name]
                for previous_field in previous_fields:
                    previous_field.field_name = document_grammar_field_name

                new_ordered_fields_lookup[
                    document_grammar_field_name
                ] = previous_fields

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
