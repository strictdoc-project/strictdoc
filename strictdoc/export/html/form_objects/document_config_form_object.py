import html
import re
from collections import defaultdict
from typing import Dict, List, Optional

from starlette.datastructures import FormData

from strictdoc.backend.sdoc.models.document import Document
from strictdoc.backend.sdoc.models.free_text import FreeText
from strictdoc.export.rst.rst_to_html_fragment_writer import (
    RstToHtmlFragmentWriter,
)
from strictdoc.helpers.auto_described import auto_described
from strictdoc.helpers.string import sanitize_html_form_field
from strictdoc.server.error_object import ErrorObject


@auto_described
class DocumentConfigFormObject(ErrorObject):
    def __init__(
        self,
        *,
        document_mid: str,
        document_title: str,
        document_uid: Optional[str],
        document_version: Optional[str],
        document_classification: Optional[str],
        document_freetext_unescaped: str,
        document_freetext_escaped: str,
    ):
        assert isinstance(document_mid, str), document_mid
        assert isinstance(document_title, str), document_title
        super().__init__()
        self.document_mid: Optional[str] = document_mid
        self.document_title: str = document_title
        self.document_uid: Optional[str] = (
            document_uid if document_uid is not None else ""
        )
        self.document_version: Optional[str] = (
            document_version if document_version is not None else ""
        )
        self.document_classification: Optional[str] = (
            document_classification
            if document_classification is not None
            else ""
        )
        self.document_freetext_unescaped = document_freetext_unescaped
        self.document_freetext_escaped = document_freetext_escaped

    @staticmethod
    def create_from_request(
        *, document_mid: str, request_form_data: FormData
    ) -> "DocumentConfigFormObject":
        config_fields: Dict[str, List[str]] = defaultdict(list)
        for field_name, field_value in request_form_data.multi_items():
            result = re.search(r"^document\[(.*)]$", field_name)
            if result is not None:
                config_fields[result.group(1)].append(field_value)
        document_title: str = (
            config_fields["TITLE"][0] if "TITLE" in config_fields else ""
        )
        document_title = sanitize_html_form_field(
            document_title, multiline=False
        )
        document_title = document_title if document_title is not None else ""

        document_uid: str = ""
        if "UID" in config_fields:
            document_uid = config_fields["UID"][0]
            document_uid = sanitize_html_form_field(
                document_uid, multiline=False
            )

        document_version: str = ""
        if "VERSION" in config_fields:
            document_version = config_fields["VERSION"][0]
            document_version = sanitize_html_form_field(
                document_version, multiline=False
            )

        document_classification: str = ""
        if "CLASSIFICATION" in config_fields:
            document_classification = config_fields["CLASSIFICATION"][0]
            document_classification = sanitize_html_form_field(
                document_classification, multiline=False
            )

        document_freetext: str = ""
        if "FREETEXT" in config_fields:
            document_freetext = config_fields["FREETEXT"][0]
            document_freetext = sanitize_html_form_field(
                document_freetext, multiline=True
            )
            document_freetext_escaped = html.escape(document_freetext)

        form_object = DocumentConfigFormObject(
            document_mid=document_mid,
            document_title=document_title,
            document_uid=document_uid,
            document_version=document_version,
            document_classification=document_classification,
            document_freetext_unescaped=document_freetext,
            document_freetext_escaped=document_freetext_escaped,
        )
        return form_object

    @staticmethod
    def create_from_document(
        *, document: Document
    ) -> "DocumentConfigFormObject":
        assert isinstance(document, Document)

        document_freetext = ""
        document_freetext_escaped = ""
        if len(document.free_texts) > 0:
            freetext: FreeText = document.free_texts[0]
            document_freetext = freetext.get_parts_as_text()
            document_freetext_escaped = html.escape(document_freetext)

        return DocumentConfigFormObject(
            document_mid=document.node_id,
            document_title=document.title,
            document_uid=document.config.uid,
            document_version=document.config.version,
            document_classification=document.config.classification,
            document_freetext_unescaped=document_freetext,
            document_freetext_escaped=document_freetext_escaped,
        )

    def validate(self, context_document: Document) -> bool:
        assert isinstance(context_document, Document)
        if len(self.document_title) == 0:
            self.add_error(
                "TITLE",
                "Document title must not be empty.",
            )

        if len(self.document_freetext_unescaped) > 0:
            (
                parsed_html,
                rst_error,
            ) = RstToHtmlFragmentWriter(
                context_document=context_document
            ).write_with_validation(self.document_freetext_unescaped)
            if parsed_html is None:
                self.add_error("FREETEXT", rst_error)

        return len(self.errors) == 0
