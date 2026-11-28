"""
Set is_composite on the nodes of a Markdown document.

This module does not import the Markdown parser or PyYAML, so that the
traceability index builder can fix up a Markdown document from the cache
without these imports.
"""

from typing import Any, List

from strictdoc.backend.sdoc.models.document import SDocDocument
from strictdoc.backend.sdoc.models.document_from_file import DocumentFromFile
from strictdoc.backend.sdoc.models.document_grammar import DocumentGrammar
from strictdoc.backend.sdoc.models.node import SDocNode
from strictdoc.helpers.cast import assert_cast


def fixup_composite_nodes(document: SDocDocument) -> None:
    # Markdown nesting is heading-level based, so it never sets
    # is_composite the way SDoc's [[TAG]]...[[/TAG]] syntax does; derive
    # it here from the (by-now fully resolved) grammar instead.
    grammar = assert_cast(document.grammar, DocumentGrammar)

    def walk(section_contents: List[Any]) -> None:
        for node_ in section_contents:
            # An included document is not resolved yet at this point. It
            # is also in the document tree on its own, so it gets its own
            # fix-up pass according to its own markup.
            if isinstance(node_, DocumentFromFile):
                continue
            if isinstance(node_, SDocNode):
                element = grammar.elements_by_type.get(node_.node_type)
                if element is not None and element.property_is_composite:
                    node_.is_composite = True
            walk(node_.section_contents)

    walk(document.section_contents)
