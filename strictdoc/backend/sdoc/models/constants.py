"""
@relation(SDOC-SRS-18, scope=file)
"""

from strictdoc.backend.sdoc.models.anchor import Anchor
from strictdoc.backend.sdoc.models.document import SDocDocument
from strictdoc.backend.sdoc.models.document_config import (
    DocumentConfig,
    DocumentCustomMetadata,
    DocumentCustomMetadataKeyValuePair,
)
from strictdoc.backend.sdoc.models.document_from_file import DocumentFromFile
from strictdoc.backend.sdoc.models.document_grammar import (
    DocumentGrammar,
    GrammarElement,
)
from strictdoc.backend.sdoc.models.document_view import (
    DocumentView,
    ViewElement,
)
from strictdoc.backend.sdoc.models.inline_link import InlineLink
from strictdoc.backend.sdoc.models.node import (
    SDocCompositeNode,
    SDocNode,
    SDocNodeField,
)
from strictdoc.backend.sdoc.models.reference import (
    ChildReqReference,
    FileEntry,
    FileReference,
    ParentReqReference,
    Reference,
)
from strictdoc.backend.sdoc.models.section import SDocSection
from strictdoc.backend.sdoc.models.type_system import (
    GrammarElementFieldMultipleChoice,
    GrammarElementFieldSingleChoice,
    GrammarElementFieldString,
    GrammarElementFieldTag,
    GrammarElementRelationChild,
    GrammarElementRelationFile,
    GrammarElementRelationParent,
    ViewElementField,
    ViewElementHiddenTag,
    ViewElementTags,
)

SECTION_MODELS = [
    SDocSection,
    DocumentFromFile,
    SDocNode,
    SDocNodeField,
    SDocCompositeNode,
    Reference,
    ParentReqReference,
    ChildReqReference,
    FileReference,
    InlineLink,
    Anchor,
    FileEntry,
]

GRAMMAR_MODELS = [
    DocumentGrammar,
    GrammarElement,
    GrammarElementFieldString,
    GrammarElementFieldSingleChoice,
    GrammarElementFieldMultipleChoice,
    GrammarElementFieldTag,
    GrammarElementRelationParent,
    GrammarElementRelationChild,
    GrammarElementRelationFile,
]

DOCUMENT_MODELS = [
    DocumentConfig,
    DocumentCustomMetadata,
    DocumentCustomMetadataKeyValuePair,
    SDocDocument,
    DocumentView,
    ViewElement,
    ViewElementField,
    ViewElementTags,
    ViewElementHiddenTag,
]
DOCUMENT_MODELS.extend(GRAMMAR_MODELS)
DOCUMENT_MODELS.extend(SECTION_MODELS)
