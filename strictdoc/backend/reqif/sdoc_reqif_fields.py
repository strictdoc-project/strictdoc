class ReqIFProfile:
    P1_SDOC = "sdoc"
    P11_POLARION = "p11_polarion"

    ALL = {P1_SDOC, P11_POLARION}


SDOC_SPEC_OBJECT_TYPE_SINGLETON = "REQUIREMENT_OR_SECTION"


class SDocRequirementReservedField:
    UID = "UID"
    TITLE = "TITLE"
    STATEMENT = "STATEMENT"
    COMMENT = "COMMENT"
    CREATED_BY = "CREATED_BY"

    SET = {UID, TITLE, STATEMENT, COMMENT, CREATED_BY}


class ReqIFRequirementReservedField:
    UID = "ReqIF.ForeignID"
    NAME = "ReqIF.Name"
    TEXT = "ReqIF.Text"
    CREATED_BY = "ReqIF.ForeignCreatedBy"

    COMMENT_NOTES = "NOTES"

    SET = {UID, NAME, TEXT, CREATED_BY, COMMENT_NOTES}


class ReqIFChapterField:
    CHAPTER_NAME = "ReqIF.ChapterName"
    TEXT = "ReqIF.Text"


SDOC_TO_REQIF_FIELD_MAP = {
    SDocRequirementReservedField.UID: ReqIFRequirementReservedField.UID,
    SDocRequirementReservedField.TITLE: ReqIFRequirementReservedField.NAME,
    SDocRequirementReservedField.STATEMENT: ReqIFRequirementReservedField.TEXT,
    SDocRequirementReservedField.COMMENT: ReqIFRequirementReservedField.COMMENT_NOTES,  # noqa: E501
    SDocRequirementReservedField.CREATED_BY: ReqIFRequirementReservedField.CREATED_BY,  # noqa: E501
}

REQIF_MAP_TO_SDOC_FIELD_MAP = {
    ReqIFRequirementReservedField.UID: SDocRequirementReservedField.UID,
    ReqIFRequirementReservedField.NAME: SDocRequirementReservedField.TITLE,
    ReqIFRequirementReservedField.TEXT: SDocRequirementReservedField.STATEMENT,
    ReqIFRequirementReservedField.COMMENT_NOTES: SDocRequirementReservedField.COMMENT,  # noqa: E501
    ReqIFRequirementReservedField.CREATED_BY: SDocRequirementReservedField.CREATED_BY,  # noqa: E501
}

DEFAULT_SDOC_GRAMMAR_FIELDS = [
    "ReqIF.ForeignID",
    "LEVEL",
    "STATUS",
    "TAGS",
    "REFS",
    "ReqIF.Name",
    "ReqIF.Text",
    "RATIONALE",
    "NOTES",
    "ReqIF.ChapterName",
]

SDOC_SPECIFICATION_TYPE_SINGLETON = "SDOC_SPECIFICATION_TYPE_SINGLETON"

SDOC_SPEC_RELATION_PARENT_TYPE_SINGLETON = (
    "SDOC_SPEC_RELATION_PARENT_TYPE_SINGLETON"
)
