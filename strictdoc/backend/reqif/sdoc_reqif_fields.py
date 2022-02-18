SDOC_SPEC_OBJECT_TYPE_SINGLETON = "REQUIREMENT_OR_SECTION"


class SDocRequirementReservedField:
    UID = "UID"
    # STATUS = "STATUS"
    TITLE = "TITLE"
    STATEMENT = "STATEMENT"
    COMMENT = "COMMENT"

    SET = {UID, TITLE, STATEMENT, COMMENT}


class ReqIFRequirementReservedField:
    UID = "ReqIF.ForeignID"
    NAME = "ReqIF.Name"
    TEXT = "ReqIF.Text"

    COMMENT_NOTES = "NOTES"

    SET = {UID, NAME, TEXT, COMMENT_NOTES}


class ReqIFChapterField:
    CHAPTER_NAME = "ReqIF.ChapterName"
    TEXT = "ReqIF.Text"


SDOC_TO_REQIF_FIELD_MAP = {
    SDocRequirementReservedField.UID: ReqIFRequirementReservedField.UID,
    SDocRequirementReservedField.TITLE: ReqIFRequirementReservedField.NAME,
    SDocRequirementReservedField.STATEMENT: ReqIFRequirementReservedField.TEXT,
    SDocRequirementReservedField.COMMENT: ReqIFRequirementReservedField.COMMENT_NOTES,  # noqa: E501
}

REQIF_MAP_TO_SDOC_FIELD_MAP = {
    ReqIFRequirementReservedField.UID: SDocRequirementReservedField.UID,
    ReqIFRequirementReservedField.NAME: SDocRequirementReservedField.TITLE,
    ReqIFRequirementReservedField.TEXT: SDocRequirementReservedField.STATEMENT,
    ReqIFRequirementReservedField.COMMENT_NOTES: SDocRequirementReservedField.COMMENT,  # noqa: E501
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
