"""
@relation(SDOC-SRS-98, SDOC-SRS-109, scope=file)
"""

from typing import Generator, List, Optional

from strictdoc.backend.sdoc.document_reference import DocumentReference
from strictdoc.backend.sdoc.models.document_config import DocumentConfig
from strictdoc.backend.sdoc.models.document_grammar import (
    DocumentGrammar,
)
from strictdoc.backend.sdoc.models.document_view import DocumentView
from strictdoc.backend.sdoc.models.grammar_element import (
    GrammarElement,
    GrammarElementField,
    GrammarElementFieldMultipleChoice,
    GrammarElementFieldSingleChoice,
    GrammarElementFieldTag,
)
from strictdoc.backend.sdoc.models.model import (
    SDocDocumentFromFileIF,
    SDocDocumentIF,
    SDocElementIF,
    SDocNodeIF,
)
from strictdoc.backend.sdoc.models.node import SDocNode
from strictdoc.core.document_meta import DocumentMeta
from strictdoc.helpers.auto_described import auto_described
from strictdoc.helpers.cast import assert_cast
from strictdoc.helpers.mid import MID
from strictdoc.helpers.ordered_set import OrderedSet


@auto_described
class SDocDocumentContext:
    def __init__(self) -> None:
        self.title_number_string: Optional[str] = None


@auto_described
class SDocDocument(SDocDocumentIF):
    def __init__(
        self,
        mid: Optional[str],
        title: str,
        config: Optional[DocumentConfig],
        view: Optional[DocumentView],
        grammar: Optional[DocumentGrammar],
        section_contents: List[SDocElementIF],
        is_bundle_document: bool = False,
    ) -> None:
        self.title: str = title
        self.reserved_title: str = title
        self.config: DocumentConfig = (
            config
            if config is not None
            else DocumentConfig.default_config(self)
        )
        self.view: DocumentView = (
            view if view is not None else DocumentView.create_default(self)
        )
        self.grammar: Optional[DocumentGrammar] = grammar
        self.section_contents: List[SDocElementIF] = section_contents

        self.is_bundle_document: bool = is_bundle_document

        self.fragments_from_files: List[SDocDocumentFromFileIF] = []

        self.ng_level: int = 0
        self.ng_has_requirements = False

        self.meta: Optional[DocumentMeta] = None

        self.reserved_mid: MID = MID(mid) if mid is not None else MID.create()
        self.mid_permanent: bool = mid is not None
        self.included_documents: List[SDocDocumentIF] = []
        self.context: SDocDocumentContext = SDocDocumentContext()

        self.ng_including_document_reference: Optional[DocumentReference] = None
        self.ng_including_document_from_file: Optional[
            SDocDocumentFromFileIF
        ] = None

    def iterate_nodes(
        self, element_type: Optional[str] = None
    ) -> Generator[SDocNodeIF, None, None]:
        """
        Iterate over all non-[TEXT] nodes in the document.

        If element_type is given, then only nodes of type `element_type` are
        returned. Otherwise, all element types are returned.
        """
        task_list: List[SDocElementIF] = list(self.section_contents)
        while task_list:
            node = task_list.pop(0)

            if isinstance(node, SDocDocumentFromFileIF):
                yield from node.iterate_nodes(element_type)

            if isinstance(node, SDocNodeIF):
                if node.node_type != "TEXT":
                    if element_type is None or node.node_type == element_type:
                        yield node

            task_list.extend(node.section_contents)

    def has_any_requirements(self) -> bool:
        return any(True for _ in self.iterate_nodes())

    def collect_options_for_tag(
        self, element_type: str, field_name: str
    ) -> List[str]:
        """
        Returns the list of existing options for a tag field in this document.
        """
        option_set: OrderedSet[str] = OrderedSet()

        for nodeif in self.iterate_nodes(element_type):
            node = assert_cast(nodeif, SDocNode)
            if field_name in node.ordered_fields_lookup:
                node_field = node.ordered_fields_lookup[field_name][0]
                field_value = node_field.get_text_value()
                if field_value:
                    options = [
                        option.strip()
                        for option in field_value.split(",")
                        if option.strip()
                    ]
                    for option in options:
                        option_set.add(option)

        return list(option_set)

    @property
    def uid(self) -> Optional[str]:
        return self.config.uid

    def is_section(self) -> bool:
        return True

    @property
    def is_root_included_document(self) -> bool:
        return self.document_is_included()

    def is_requirement(self) -> bool:
        return False

    def get_display_node_type(self) -> str:
        return "Document"

    def get_node_type_string(self) -> Optional[str]:
        return None

    def get_type_string(self) -> str:
        return "document" if not self.document_is_included() else "section"

    def get_debug_info(self) -> str:
        debug_components: List[str] = [f"TITLE = '{self.title}'"]
        if self.meta is not None:
            debug_components.append(
                f" ({self.meta.input_doc_rel_path.relative_path})"
            )
        return f"Document({', '.join(debug_components)})"

    def document_is_included(self) -> bool:
        if self.ng_including_document_reference is None:
            return False
        return self.ng_including_document_reference.get_document() is not None

    def get_including_document(self) -> Optional["SDocDocumentIF"]:
        if self.ng_including_document_reference is None:
            return None
        return self.ng_including_document_reference.get_document()

    def iterate_included_documents_depth_first(
        self,
    ) -> Generator["SDocDocument", None, None]:
        for included_document_ in self.included_documents:
            yield included_document_
            yield from included_document_.iterate_included_documents_depth_first()

    @property
    def reserved_uid(self) -> Optional[str]:
        return self.config.uid

    def assign_meta(self, meta: DocumentMeta) -> None:
        assert isinstance(meta, DocumentMeta)
        self.meta = meta

    def has_any_nodes(self) -> bool:
        return len(self.section_contents) > 0

    def get_display_title(
        self,
        include_toc_number: bool = True,  # noqa: ARG002
    ) -> str:
        return self.title

    @property
    def ng_resolved_custom_level(self) -> Optional[str]:
        return None

    @property
    def requirement_prefix(self) -> str:
        return self.get_prefix()

    def get_prefix(self) -> str:
        return self.config.get_prefix()

    def get_prefix_for_new_node(self, node_type: str) -> Optional[str]:
        assert isinstance(node_type, str) and len(node_type), node_type

        grammar: DocumentGrammar = assert_cast(self.grammar, DocumentGrammar)
        element: GrammarElement = grammar.elements_by_type[node_type]
        if (element_prefix := element.property_prefix) is not None:
            if element_prefix == "None":
                return None
            return element_prefix

        return self.get_prefix()

    def enumerate_meta_field_titles(self) -> Generator[str, None, None]:
        assert self.grammar is not None
        assert self.grammar.elements is not None
        # FIXME: currently only enumerating a single element ([0])
        yield from self.grammar.elements[0].enumerate_meta_field_titles()

    def enumerate_custom_content_field_titles(
        self,
    ) -> Generator[str, None, None]:
        assert self.grammar is not None
        assert self.grammar.elements is not None
        # FIXME: currently only enumerating a single element ([0])
        yield from self.grammar.elements[
            0
        ].enumerate_custom_content_field_titles()

    def get_grammar_element_field_for(
        self, element_type: str, field_name: str
    ) -> GrammarElementField:
        """
        Returns the GrammarElementField for a field of a [element_type] in this document.
        """
        grammar: DocumentGrammar = assert_cast(self.grammar, DocumentGrammar)
        element: GrammarElement = grammar.elements_by_type[element_type]
        field: GrammarElementField = element.fields_map[field_name]
        return field

    def get_options_for_field(
        self, element_type: str, field_name: str
    ) -> List[str]:
        """
        Returns the list of valid options for a Single/MultiChoice field in this document.
        """
        field: GrammarElementField = self.get_grammar_element_field_for(
            element_type, field_name
        )

        if isinstance(field, GrammarElementFieldSingleChoice) or isinstance(
            field, GrammarElementFieldMultipleChoice
        ):
            return field.options

        if isinstance(field, GrammarElementFieldTag):
            return self.collect_options_for_tag(element_type, field_name)

        raise AssertionError(f"Must not reach here: {field}")
