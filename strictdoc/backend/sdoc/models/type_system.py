import os
from typing import List, Optional

from pybtex.database import Entry

from strictdoc.helpers.auto_described import auto_described


class RequirementFieldName:
    UID = "UID"
    LEVEL = "LEVEL"
    STATUS = "STATUS"
    TAGS = "TAGS"
    REFS = "REFS"
    TITLE = "TITLE"
    STATEMENT = "STATEMENT"
    RATIONALE = "RATIONALE"
    COMMENT = "COMMENT"


RESERVED_NON_META_FIELDS = [
    RequirementFieldName.REFS,
    RequirementFieldName.TITLE,
    RequirementFieldName.STATEMENT,
    RequirementFieldName.COMMENT,
    RequirementFieldName.RATIONALE,
    RequirementFieldName.LEVEL,
]


class RequirementFieldType:
    STRING = "String"
    SINGLE_CHOICE = "SingleChoice"
    MULTIPLE_CHOICE = "MultipleChoice"
    TAG = "Tag"
    REFERENCE = "Reference"


class GrammarReferenceType:
    PARENT_REQ_REFERENCE = "ParentReqReference"
    FILE_REFERENCE = "FileReference"
    BIB_REFERENCE = "BibReference"


@auto_described
class FileEntry:
    def __init__(self, parent, file_format: Optional[str], file_path: str):
        self.parent = parent
        self.file_format = file_format  # Default: FileEntryFormat.SOURCECODE
        self.file_path = file_path

        path_forward_slashes = file_path.replace("\\", "/")
        self.path_forward_slashes = path_forward_slashes
        self.path_normalized = os.path.normpath(path_forward_slashes)


class FileEntryFormat:
    SOURCECODE = "Sourcecode"
    PYTHON = "Python"


class BibEntryFormat:
    STRING = "String"
    BIBTEX = "BibTex"
    CITATION = "Citation"


@auto_described
class BibEntry:
    def __init__(self, parent, bib_format: Optional[str], bib_value: str):
        self.parent = parent
        self.bib_format = bib_format or BibEntryFormat.STRING
        self.bib_value = bib_value
        self.ref_cite = None
        self.ref_detail = None
        self.bibtex_entry = None

        if self.bib_format == BibEntryFormat.STRING:
            # <CitationKey>, <Entry details>
            # Note: A STRING entry is converted in a BibTex @misc entry type
            # where the details are put in the Entries "note" field.
            # An empty details field is treated as a Citation!
            cite, detail = (
                bib_value.split(",", 1) if "," in bib_value else (bib_value, "")
            )
            self.ref_cite = cite.strip()
            self.ref_detail = (
                detail.strip()
                if (isinstance(detail, str) and len(detail) > 0)
                else None
            )
            if self.ref_detail:
                self.bibtex_entry = Entry(
                    "misc", fields={"note": self.ref_detail}
                )
                self.bibtex_entry.key = self.ref_cite
            # TODO In case of a Citation, Verify/Reference the cited BibEntry

        elif self.bib_format == BibEntryFormat.BIBTEX:
            # @<BibTex entry type>{<CitationKey>, <BibTex key-value pairs>}
            self.bibtex_entry = Entry.from_string(bib_value, "bibtex")
            self.ref_cite = self.bibtex_entry.key

        elif self.bib_format == BibEntryFormat.CITATION:
            # <CitationKey>[, <Reference details>]
            # Ref.Details may include additional info about the subsection,
            # paragraph, page(s), etc. to be referenced, not already included
            # in the cited BibTex entry
            cite, detail = (
                bib_value.split(",", 1) if "," in bib_value else (bib_value, "")
            )
            self.ref_cite = cite.strip()
            self.ref_detail = (
                detail.strip()
                if (isinstance(detail, str) and len(detail) > 0)
                else None
            )
            # TODO Verify/Reference the cited BibEntry


class ReferenceType:
    PARENT = "Parent"
    FILE = "File"
    BIB_REF = "BibRef"

    GRAMMAR_REFERENCE_TYPE_MAP = {
        PARENT: GrammarReferenceType.PARENT_REQ_REFERENCE,
        FILE: GrammarReferenceType.FILE_REFERENCE,
        BIB_REF: GrammarReferenceType.BIB_REFERENCE,
    }


@auto_described
class GrammarElementField:
    def __init__(self):
        self.title: str = ""
        self.gef_type: str = ""
        self.required: bool = False


@auto_described
class GrammarElementFieldString(GrammarElementField):
    def __init__(self, parent, title: str, required: str):
        super().__init__()
        self.parent = parent
        self.title: str = title
        self.gef_type = RequirementFieldType.STRING
        self.required: bool = required == "True"


@auto_described
class GrammarElementFieldSingleChoice(GrammarElementField):
    def __init__(self, parent, title: str, options: List[str], required: str):
        super().__init__()
        self.parent = parent
        self.title: str = title
        self.gef_type = RequirementFieldType.SINGLE_CHOICE
        self.options: List[str] = options
        self.required: bool = required == "True"


@auto_described
class GrammarElementFieldMultipleChoice(GrammarElementField):
    def __init__(self, parent, title: str, options: List[str], required: str):
        super().__init__()
        self.parent = parent
        self.title: str = title
        self.gef_type = RequirementFieldType.MULTIPLE_CHOICE
        self.options: List[str] = options
        self.required: bool = required == "True"


@auto_described
class GrammarElementFieldTag(GrammarElementField):
    def __init__(self, parent, title: str, required: str):
        super().__init__()
        self.parent = parent
        self.title: str = title
        self.gef_type = RequirementFieldType.TAG
        self.required: bool = required == "True"


@auto_described
class GrammarElementFieldReference(GrammarElementField):
    def __init__(self, parent, title: str, types: List[str], required: str):
        super().__init__()
        self.parent = parent
        self.gef_type = RequirementFieldType.REFERENCE
        self.title: str = title
        self.types: List[str] = types
        self.required: bool = required == "True"
