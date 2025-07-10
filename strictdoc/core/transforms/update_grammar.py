# mypy: disable-error-code="union-attr"
from typing import Dict, List

from strictdoc.backend.sdoc.models.document import SDocDocument
from strictdoc.backend.sdoc.models.document_grammar import (
    DocumentGrammar,
)
from strictdoc.backend.sdoc.models.grammar_element import GrammarElement
from strictdoc.core.traceability_index import (
    TraceabilityIndex,
)
from strictdoc.export.html.form_objects.grammar_form_object import (
    GrammarFormObject,
)


class UpdateGrammarCommand:
    def __init__(
        self,
        *,
        form_object: GrammarFormObject,
        document: SDocDocument,
        traceability_index: TraceabilityIndex,
    ):
        self.form_object: GrammarFormObject = form_object
        self.document: SDocDocument = document
        self.traceability_index: TraceabilityIndex = traceability_index

    def perform(self) -> bool:
        form_object: GrammarFormObject = self.form_object
        document: SDocDocument = self.document

        form_element_names = map(
            lambda field_: field_.field_name, form_object.fields
        )

        map_existing_elements_by_name: Dict[str, GrammarElement] = {}
        for grammar_element_ in document.grammar.elements:
            map_existing_elements_by_name[grammar_element_.tag] = (
                grammar_element_
            )

        updated_grammar_elements: List[GrammarElement] = []
        for form_element_name_ in form_element_names:
            if form_element_name_ in map_existing_elements_by_name:
                updated_grammar_elements.append(
                    map_existing_elements_by_name[form_element_name_]
                )
            else:
                updated_grammar_elements.append(
                    GrammarElement.create_default(form_element_name_)
                )

        new_grammar = DocumentGrammar(
            parent=document, elements=updated_grammar_elements
        )
        document.grammar = new_grammar

        return True
