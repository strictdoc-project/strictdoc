"""
@relation(SDOC-SRS-110, SDOC-SRS-151, scope=file)
"""

from typing import TYPE_CHECKING, Any, List, Optional, Tuple

from strictdoc.backend.sdoc.constants import SDocMarkup
from strictdoc.backend.sdoc.models.inline_link import InlineLink
from strictdoc.helpers.auto_described import auto_described

if TYPE_CHECKING:
    from strictdoc.backend.sdoc.models.document import SDocDocument


@auto_described
class DocumentCustomMetadataKeyValuePair:
    def __init__(
        self,
        *,
        parent: Optional["DocumentCustomMetadata"] = None,
        key: Optional[str],
        parts: List[Any],
    ) -> None:
        self.parent: Optional[DocumentCustomMetadata] = parent
        self.key = key
        self.parts: List[Any] = parts
        for part in parts:
            if isinstance(part, InlineLink):
                part.parent = self

    def get_text_value(self) -> str:
        text = ""
        for part in self.parts:
            if isinstance(part, str):
                text += part
            elif isinstance(part, InlineLink):
                text += "[LINK: "
                text += part.link
                text += "]"
            else:
                raise NotImplementedError(part)  # pragma: no cover
        return text

    def get_owning_node(self) -> "SDocDocument":
        assert self.parent is not None
        assert self.parent.parent is not None
        document = self.parent.parent.parent
        assert document is not None
        return document


@auto_described
class DocumentCustomMetadata:
    def __init__(
        self,
        *,
        parent: Optional["DocumentConfig"] = None,
        entries: List[DocumentCustomMetadataKeyValuePair],
    ) -> None:
        self.parent: Optional[DocumentConfig] = parent
        self.entries: List[DocumentCustomMetadataKeyValuePair] = entries


@auto_described
class DocumentConfig:
    @staticmethod
    def default_config(document: Optional["SDocDocument"]) -> "DocumentConfig":
        return DocumentConfig(
            parent=document,
            version=None,
            date=None,
            uid=None,
            classification=None,
            requirement_prefix=None,
            root=None,
            enable_mid=None,
            relation_field=None,
            markup=None,
            auto_levels=None,
            layout=None,
            requirement_style=None,
            requirement_in_toc=None,
            default_view=None,
            custom_metadata=None,
        )

    def __init__(
        self,
        *,
        parent: Optional["SDocDocument"],
        version: Optional[str],
        date: Optional[str],
        uid: Optional[str],
        classification: Optional[str],
        requirement_prefix: Optional[str],
        root: Optional[str],
        enable_mid: Optional[str],
        relation_field: Optional[str],
        markup: Optional[str],
        auto_levels: Optional[str],
        layout: Optional[str],
        requirement_style: Optional[str],
        requirement_in_toc: Optional[str],
        default_view: Optional[str],
        custom_metadata: Optional[DocumentCustomMetadata],
        view_style_tag: Optional[str] = None,
        node_in_toc_tag: Optional[str] = None,
    ) -> None:
        self.parent = parent
        self.version: Optional[str] = version
        self.date: Optional[str] = date

        meaningful_uid: Optional[str] = None
        if uid is not None and len(uid) > 0:
            meaningful_uid = uid
        self.uid: Optional[str] = meaningful_uid

        self.classification: Optional[str] = classification
        self.requirement_prefix: Optional[str] = requirement_prefix

        self.root: Optional[bool] = (
            True if root == "True" else (False if root == "False" else None)
        )
        self.enable_mid: Optional[bool] = (
            True
            if enable_mid == "True"
            else (False if root == "False" else None)
        )
        self.relation_field: Optional[str] = (
            relation_field
            if relation_field is not None and len(relation_field) > 0
            else None
        )

        self.markup: Optional[str] = markup
        self.auto_levels: bool = auto_levels is None or auto_levels == "On"

        if layout is not None:
            if len(layout) > 0:
                assert layout in ("Default", "Website")
            else:
                layout = None
        self.layout: Optional[str] = layout

        # Possible requirement styles:
        # Simple, Table, Rows.
        self.requirement_style: Optional[str] = requirement_style
        self.view_style_tag: Optional[str] = view_style_tag

        self.requirement_in_toc: Optional[str] = requirement_in_toc
        self.node_in_toc_tag: Optional[str] = node_in_toc_tag

        self.default_view: Optional[str] = default_view
        self.ng_auto_levels_specified = auto_levels is not None

        self.ng_line_start: int = 0
        self.ng_col_start: int = 0

        self.custom_metadata: Optional[DocumentCustomMetadata] = custom_metadata

    def get_markup(self) -> str:
        if self.markup is None:
            return SDocMarkup.RST
        return self.markup

    def get_requirement_style_mode(self) -> str:
        if (
            self.requirement_style is None
            or self.requirement_style == "Narrative"
        ):
            return "narrative"
        if self.requirement_style == "Plain":
            return "plain"
        if self.requirement_style in (
            "Inline",
            "Simple",
        ):
            return "simple"
        if self.requirement_style == "Table":
            return "table"
        if self.requirement_style == "Zebra":
            return "zebra"
        raise NotImplementedError(self.requirement_style)

    def is_requirement_in_toc(self) -> bool:
        return (
            self.requirement_in_toc is None or self.requirement_in_toc == "True"
        )

    def get_prefix(self) -> str:
        if self.requirement_prefix is not None:
            return self.requirement_prefix
        return "REQ-"

    def get_relation_field(self) -> str:
        return self.relation_field or "UID"

    def has_meta(self) -> bool:
        # TODO: When OPTIONS are not provided to a document, the self.number and
        # self.version are both None. Otherwise, they become empty strings "".
        # This issue might deserve a bug report to TextX.
        return (
            (self.uid is not None and len(self.uid) > 0)
            or (self.version is not None and len(self.version) > 0)
            or (
                self.classification is not None and len(self.classification) > 0
            )
        )

    def has_custom_metadata(self) -> bool:
        return len(self.get_custom_metadata()) > 0

    def get_custom_metadata(self) -> List[Tuple[str, str]]:
        if (
            self.custom_metadata is not None
            and self.custom_metadata.entries is not None
        ):
            reserved_keys = {
                key
                for key, value in (
                    ("UID", self.uid),
                    ("VERSION", self.version),
                    ("DATE", self.date),
                    ("CLASSIFICATION", self.classification),
                )
                if value is not None and len(value) > 0
            }
            return [
                (entry.key, entry.get_text_value())
                for entry in self.custom_metadata.entries
                if entry.key is not None
                and entry.key.upper() not in reserved_keys
            ]
        return []
