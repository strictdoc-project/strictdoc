from strictdoc.backend.sdoc.models.document import Document
from strictdoc.backend.sdoc.models.document_config import DocumentConfig
from strictdoc.backend.sdoc.models.document_grammar import (
    DocumentGrammar,
    GrammarElement,
)
from strictdoc.backend.sdoc.models.fragment import Fragment
from strictdoc.backend.sdoc.models.fragment_from_file import FragmentFromFile
from strictdoc.backend.sdoc.models.inline_link import InlineLink
from strictdoc.backend.sdoc.models.reference import (
    BibReference,
    FileReference,
    ParentReqReference,
    Reference,
)
from strictdoc.backend.sdoc.models.requirement import (
    CompositeRequirement,
    Requirement,
    RequirementField,
)
from strictdoc.backend.sdoc.models.section import FreeText, Section
from strictdoc.backend.sdoc.models.type_system import (
    BibEntry,
    FileEntry,
    GrammarElementFieldMultipleChoice,
    GrammarElementFieldReference,
    GrammarElementFieldSingleChoice,
    GrammarElementFieldString,
    GrammarElementFieldTag,
)

SECTION_MODELS = [
    Section,
    FragmentFromFile,
    Requirement,
    RequirementField,
    CompositeRequirement,
    Reference,
    ParentReqReference,
    FileReference,
    BibReference,
    FreeText,
    InlineLink,
    FileEntry,
    BibEntry,
]

DOCUMENT_MODELS = [
    DocumentConfig,
    Document,
    DocumentGrammar,
    GrammarElement,
    GrammarElementFieldString,
    GrammarElementFieldSingleChoice,
    GrammarElementFieldMultipleChoice,
    GrammarElementFieldTag,
    GrammarElementFieldReference,
]
DOCUMENT_MODELS.extend(SECTION_MODELS)

INCLUDE_MODELS = [
    Fragment,
]
INCLUDE_MODELS.extend(SECTION_MODELS)
