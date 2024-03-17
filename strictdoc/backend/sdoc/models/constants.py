from strictdoc.backend.sdoc.models.anchor import Anchor
from strictdoc.backend.sdoc.models.document import SDocDocument
from strictdoc.backend.sdoc.models.document_bibliography import (
    DocumentBibliography,
)
from strictdoc.backend.sdoc.models.document_config import DocumentConfig
from strictdoc.backend.sdoc.models.document_from_file import FragmentFromFile
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
    CompositeRequirement,
    SDocNode,
    SDocNodeField,
)
from strictdoc.backend.sdoc.models.reference import (
    BibReference,
    ChildReqReference,
    FileReference,
    ParentReqReference,
    Reference,
)
from strictdoc.backend.sdoc.models.section import FreeText, SDocSection
from strictdoc.backend.sdoc.models.type_system import (
    BibEntry,
    BibFileEntry,
    FileEntry,
    GrammarElementFieldMultipleChoice,
    GrammarElementFieldReference,
    GrammarElementFieldSingleChoice,
    GrammarElementFieldString,
    GrammarElementFieldTag,
    GrammarElementRelationBibtex,
    GrammarElementRelationChild,
    GrammarElementRelationFile,
    GrammarElementRelationParent,
    ViewElementField,
    ViewElementHiddenTag,
    ViewElementTags,
)

SECTION_MODELS = [
    SDocSection,
    FragmentFromFile,
    SDocNode,
    SDocNodeField,
    CompositeRequirement,
    Reference,
    ParentReqReference,
    ChildReqReference,
    FileReference,
    BibReference,
    FreeText,
    InlineLink,
    Anchor,
    BibFileEntry,
    FileEntry,
    BibEntry,
]

DOCUMENT_MODELS = [
    DocumentConfig,
    SDocDocument,
    DocumentGrammar,
    DocumentView,
    DocumentBibliography,
    GrammarElement,
    GrammarElementFieldString,
    GrammarElementFieldSingleChoice,
    GrammarElementFieldMultipleChoice,
    GrammarElementFieldTag,
    GrammarElementFieldReference,
    GrammarElementRelationBibtex,
    GrammarElementRelationParent,
    GrammarElementRelationChild,
    GrammarElementRelationFile,
    ViewElement,
    ViewElementField,
    ViewElementTags,
    ViewElementHiddenTag,
]
DOCUMENT_MODELS.extend(SECTION_MODELS)
