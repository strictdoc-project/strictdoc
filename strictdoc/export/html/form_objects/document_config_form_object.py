# mypy: disable-error-code="no-untyped-call,no-untyped-def"
import re
from collections import defaultdict
from typing import Dict, List, Optional

from starlette.datastructures import FormData

from strictdoc.backend.sdoc.models.document import SDocDocument
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

        form_object = DocumentConfigFormObject(
            document_mid=document_mid,
            document_title=document_title,
            document_uid=document_uid,
            document_version=document_version,
            document_classification=document_classification,
        )
        return form_object

    @staticmethod
    def create_from_document(
        *,
        document: SDocDocument,
    ) -> "DocumentConfigFormObject":
        assert isinstance(document, SDocDocument)

        return DocumentConfigFormObject(
            document_mid=document.reserved_mid,
            document_title=document.title,
            document_uid=document.config.uid,
            document_version=document.config.version,
            document_classification=document.config.classification,
        )
