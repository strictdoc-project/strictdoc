from typing import List, Optional, Union

from pybtex.database import Entry

from strictdoc.helpers.auto_described import auto_described
from strictdoc.helpers.mid import MID


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
    CHILD_REQ_REFERENCE = "ChildReqReference"
    FILE_REFERENCE = "FileReference"
    BIB_REFERENCE = "BibReference"


@auto_described
class FileEntry:
    def __init__(self, parent, g_file_format: Optional[str], g_file_path: str):
        self.parent = parent

        # Default: FileEntryFormat.SOURCECODE  # noqa: ERA001
        self.g_file_format: Optional[str] = g_file_format

        # TODO: Might be worth to prohibit the use of Windows paths altogether.
        self.g_file_path: str = g_file_path
        file_path_posix = g_file_path.replace("\\", "/")
        self.file_path_posix = file_path_posix


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
    CHILD = "Child"
    FILE = "File"
    BIB_REF = "BibTex"

    GRAMMAR_REFERENCE_TYPE_MAP = {
        PARENT: GrammarReferenceType.PARENT_REQ_REFERENCE,
        CHILD: GrammarReferenceType.CHILD_REQ_REFERENCE,
        FILE: GrammarReferenceType.FILE_REFERENCE,
        BIB_REF: GrammarReferenceType.BIB_REFERENCE,
    }


@auto_described
class GrammarElementField:
    def __init__(self):
        self.title: str = ""
        self.gef_type: str = ""
        self.required: bool = False
        self.mid: MID = MID.create()


@auto_described
class GrammarElementFieldString(GrammarElementField):
    def __init__(self, parent, title: str, required: str):
        super().__init__()
        self.parent = parent
        self.title: str = title
        self.gef_type = RequirementFieldType.STRING
        self.required: bool = required == "True"
        self.mid: MID = MID.create()


@auto_described
class GrammarElementFieldSingleChoice(GrammarElementField):
    def __init__(self, parent, title: str, options: List[str], required: str):
        super().__init__()
        self.parent = parent
        self.title: str = title
        self.gef_type = RequirementFieldType.SINGLE_CHOICE
        self.options: List[str] = options
        self.required: bool = required == "True"
        self.mid: MID = MID.create()


@auto_described
class GrammarElementFieldMultipleChoice(GrammarElementField):
    def __init__(self, parent, title: str, options: List[str], required: str):
        super().__init__()
        self.parent = parent
        self.title: str = title
        self.gef_type = RequirementFieldType.MULTIPLE_CHOICE
        self.options: List[str] = options
        self.required: bool = required == "True"
        self.mid: MID = MID.create()


@auto_described
class GrammarElementFieldTag(GrammarElementField):
    def __init__(self, parent, title: str, required: str):
        super().__init__()
        self.parent = parent
        self.title: str = title
        self.gef_type = RequirementFieldType.TAG
        self.required: bool = required == "True"
        self.mid: MID = MID.create()


@auto_described
class GrammarElementRelationParent:
    def __init__(
        self, parent, relation_type: str, relation_role: Optional[str]
    ):
        assert relation_type == "Parent"
        self.parent = parent
        self.relation_type = relation_type
        self.relation_role: Optional[str] = (
            relation_role
            if relation_role is not None and len(relation_role) > 0
            else None
        )
        self.mid: MID = MID.create()

    def __eq__(self, other):
        if not isinstance(other, GrammarElementRelationParent):
            raise NotImplementedError(self, other)
        return (
            self.mid == other.mid
            and self.relation_type == other.relation_type
            and self.relation_role == other.relation_role
        )


@auto_described
class GrammarElementRelationChild:
    def __init__(
        self, parent, relation_type: str, relation_role: Optional[str]
    ):
        assert relation_type == "Child"
        self.parent = parent
        self.relation_type = relation_type
        self.relation_role: Optional[str] = (
            relation_role
            if relation_role is not None and len(relation_role) > 0
            else None
        )
        self.mid: MID = MID.create()


@auto_described
class GrammarElementRelationFile:
    def __init__(self, parent, relation_type: str):
        assert relation_type == "File"
        self.parent = parent
        self.relation_type = relation_type
        self.relation_role: Optional[str] = None
        self.mid: MID = MID.create()


@auto_described
class GrammarElementRelationBibtex:
    def __init__(self, parent, relation_type: str):
        assert relation_type == "BibTex"
        self.parent = parent
        self.relation_type = relation_type
        self.relation_role: Optional[str] = None
        self.mid: MID = MID.create()


@auto_described
class GrammarElementFieldReference(GrammarElementField):
    def __init__(self, parent, title: str, types: List[str], required: str):
        super().__init__()
        self.parent = parent
        self.gef_type = RequirementFieldType.REFERENCE
        self.title: str = title
        self.types: List[str] = types
        self.required: bool = required == "True"

    def convert_to_relations(
        self,
    ) -> List[
        Union[
            GrammarElementRelationParent,
            GrammarElementRelationChild,
            GrammarElementRelationFile,
            GrammarElementRelationBibtex,
        ]
    ]:
        relation_types: List[
            Union[
                GrammarElementRelationParent,
                GrammarElementRelationChild,
                GrammarElementRelationFile,
                GrammarElementRelationBibtex,
            ]
        ] = []

        for ref_type in self.types:
            if ref_type == "ParentReqReference":
                relation_types.append(
                    GrammarElementRelationParent(
                        self.parent, "Parent", relation_role=None
                    )
                )
                continue
            if ref_type == "ChildReqReference":
                relation_types.append(
                    GrammarElementRelationChild(
                        self.parent, "Child", relation_role=None
                    )
                )
                continue
            if ref_type == "FileReference":
                relation_types.append(
                    GrammarElementRelationFile(self.parent, "File")
                )
                continue
            if ref_type == "BibReference":
                relation_types.append(
                    GrammarElementRelationBibtex(self.parent, "BibTex")
                )
                continue
            raise NotImplementedError(ref_type)
        return relation_types
