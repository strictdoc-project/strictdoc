SDOC_SPEC_OBJECT_TYPE_SINGLETON = "REQUIREMENT_OR_SECTION"


class SDocRequirementReservedField:
    UID = "UID"
    # STATUS = "STATUS"
    TITLE = "TITLE"
    STATEMENT = "STATEMENT"
    # COMMENT = "COMMENT"

    SET = {UID, TITLE, STATEMENT}


class ReqIFRequirementReservedField:
    UID = "ReqIF.ForeignID"
    NAME = "ReqIF.Name"
    TEXT = "ReqIF.Text"

    SET = {UID, NAME, TEXT}


class ReqIFChapterField:
    CHAPTER_NAME = "ReqIF.ChapterName"
    TEXT = "ReqIF.Text"


SDOC_TO_REQIF_FIELD_MAP = {
    SDocRequirementReservedField.UID: ReqIFRequirementReservedField.UID,
    SDocRequirementReservedField.TITLE: ReqIFRequirementReservedField.NAME,
    SDocRequirementReservedField.STATEMENT: ReqIFRequirementReservedField.TEXT,
}

REQIF_MAP_TO_SDOC_FIELD_MAP = {
    ReqIFRequirementReservedField.UID: SDocRequirementReservedField.UID,
    ReqIFRequirementReservedField.NAME: SDocRequirementReservedField.TITLE,
    ReqIFRequirementReservedField.TEXT: SDocRequirementReservedField.STATEMENT,
}

DEFAULT_SDOC_GRAMMAR_FIELDS = [
    "ReqIF.ForeignID",
    "LEVEL",
    "STATUS",
    "TAGS",
    "SPECIAL_FIELDS",
    "REFS",
    "ReqIF.Name",
    "ReqIF.Text",
    "BODY",
    "RATIONALE",
    "COMMENT",
    "ReqIF.ChapterName",
]
