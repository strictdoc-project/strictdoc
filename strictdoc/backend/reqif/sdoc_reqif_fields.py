"""
@relation(SDOC-SRS-72, scope=file)
"""


class ReqIFProfile:
    P01_SDOC = "p01_sdoc"

    ALL = [P01_SDOC]


SDOC_SPEC_OBJECT_TYPE_SINGLETON = "REQUIREMENT_OR_SECTION"


class SDocRequirementReservedField:
    UID = "UID"
    TITLE = "TITLE"
    STATEMENT = "STATEMENT"
    COMMENT = "COMMENT"
    CREATED_BY = "CREATED_BY"


class ReqIFReservedField:
    """
    Captures some of the most important field naming conventions by ReqIF.
    """

    UID = "ReqIF.ForeignID"

    # The chapter name appears with elements that represent chapters/sections.
    # The name usually appears with non-section elements.
    CHAPTER_NAME = "ReqIF.ChapterName"
    NAME = "ReqIF.Name"

    TEXT = "ReqIF.Text"

    CREATED_BY = "ReqIF.ForeignCreatedBy"
    COMMENT_NOTES = "NOTES"


SDOC_TO_REQIF_FIELD_MAP = {
    SDocRequirementReservedField.UID: ReqIFReservedField.UID,
    SDocRequirementReservedField.STATEMENT: ReqIFReservedField.TEXT,
    SDocRequirementReservedField.COMMENT: ReqIFReservedField.COMMENT_NOTES,
    SDocRequirementReservedField.CREATED_BY: ReqIFReservedField.CREATED_BY,
}

REQIF_MAP_TO_SDOC_FIELD_MAP = {
    ReqIFReservedField.UID: SDocRequirementReservedField.UID,
    ReqIFReservedField.NAME: SDocRequirementReservedField.TITLE,
    ReqIFReservedField.CHAPTER_NAME: SDocRequirementReservedField.TITLE,
    ReqIFReservedField.TEXT: SDocRequirementReservedField.STATEMENT,
    ReqIFReservedField.COMMENT_NOTES: SDocRequirementReservedField.COMMENT,
    ReqIFReservedField.CREATED_BY: SDocRequirementReservedField.CREATED_BY,
}

DEFAULT_SDOC_GRAMMAR_FIELDS = [
    "ReqIF.ForeignID",
    "LEVEL",
    "STATUS",
    "TAGS",
    "ReqIF.Name",
    "ReqIF.Text",
    "RATIONALE",
    "NOTES",
    "ReqIF.ChapterName",
]

SDOC_SPECIFICATION_TYPE_SINGLETON = "SDOC_SPECIFICATION_TYPE_SINGLETON"


def map_sdoc_field_title_to_reqif_field_title(
    sdoc_field_title: str, is_composite: bool
) -> str:
    """
    Map how SDoc field titles are converted to ReqIF field titles.
    """

    # Assumption: The composite types will most of the type be chapters/sections,
    # so mapping them to ReqIF Chapter Name.
    # If a user requires a more distinct mapping, we would need to introduce
    # a configuration parameter with an explicit map.
    if sdoc_field_title == "TITLE":
        if is_composite:
            return ReqIFReservedField.CHAPTER_NAME
        return ReqIFReservedField.NAME
    return SDOC_TO_REQIF_FIELD_MAP.get(sdoc_field_title) or sdoc_field_title


def map_reqif_field_title_to_sdoc_field_title(reqif_field_title: str) -> str:
    return (
        REQIF_MAP_TO_SDOC_FIELD_MAP.get(reqif_field_title) or reqif_field_title
    )
