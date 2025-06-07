# mypy: disable-error-code="no-untyped-call,no-untyped-def"
from typing import Dict, List, Optional

from starlette.datastructures import FormData

from strictdoc.backend.sdoc.models.document import SDocDocument
from strictdoc.helpers.auto_described import auto_described
from strictdoc.helpers.cast import assert_cast
from strictdoc.helpers.form_data import ParsedFormData, parse_form_data
from strictdoc.helpers.mid import MID
from strictdoc.helpers.string import sanitize_html_form_field
from strictdoc.server.error_object import ErrorObject


@auto_described
class DocumentMetadataFormField:
    def __init__(
        self,
        field_mid: str,
        field_name: str,
        field_value: str,
    ):
        assert isinstance(field_value, str)
        self.field_mid: str = field_mid
        self.field_name: str = field_name
        self.field_value: str = field_value

    @staticmethod
    def create_from_document(name: str, value: str):
        return DocumentMetadataFormField(
            field_mid=MID.create(), field_name=name, field_value=value
        )

    def get_input_field_name(self):
        return f"metadata[{self.field_mid}][name]"

    def get_input_field_value(self):
        return f"metadata[{self.field_mid}][value]"


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
        document_requirement_prefix: Optional[str],
        document_custom_metadata_fields: List[DocumentMetadataFormField],
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
        self.document_requirement_prefix: Optional[str] = (
            document_requirement_prefix
            if document_requirement_prefix is not None
            else ""
        )
        self.custom_metadata_fields: List[DocumentMetadataFormField] = (
            document_custom_metadata_fields
        )

    @staticmethod
    def create_from_request(
        *, document_mid: str, request_form_data: FormData
    ) -> "DocumentConfigFormObject":
        request_form_data_as_list = [
            (field_name, field_value)
            for field_name, field_value in request_form_data.multi_items()
        ]
        request_form_dict: ParsedFormData = assert_cast(
            parse_form_data(request_form_data_as_list), dict
        )

        config_fields: Dict[str, str] = assert_cast(
            request_form_dict["document"], dict
        )

        metadata_fields: Dict[str, Dict[str, str]] = (
            assert_cast(request_form_dict["metadata"], dict)
            if "metadata" in request_form_dict
            else {}
        )

        document_title: str = (
            config_fields["TITLE"] if "TITLE" in config_fields else ""
        )
        document_title = sanitize_html_form_field(
            document_title, multiline=False
        )
        document_title = document_title if document_title is not None else ""

        document_uid: str = ""
        if "UID" in config_fields:
            document_uid = config_fields["UID"]
            document_uid = sanitize_html_form_field(
                document_uid, multiline=False
            )

        document_version: str = ""
        if "VERSION" in config_fields:
            document_version = config_fields["VERSION"]
            document_version = sanitize_html_form_field(
                document_version, multiline=False
            )

        document_classification: str = ""
        if "CLASSIFICATION" in config_fields:
            document_classification = config_fields["CLASSIFICATION"]
            document_classification = sanitize_html_form_field(
                document_classification, multiline=False
            )

        document_requirement_prefix: str = ""
        if "PREFIX" in config_fields:
            document_requirement_prefix = config_fields["PREFIX"]
            document_requirement_prefix = sanitize_html_form_field(
                document_requirement_prefix, multiline=False
            )

        document_custom_metadata_fields: List[DocumentMetadataFormField] = []
        for field_mid, field_dict in metadata_fields.items():
            assert isinstance(field_dict, dict), type(field_dict)

            field_name = field_dict["name"].strip()
            field_value = field_dict["value"].strip()

            document_custom_metadata_field = DocumentMetadataFormField(
                field_mid=field_mid,
                field_name=field_name,
                field_value=field_value,
            )
            document_custom_metadata_fields.append(
                document_custom_metadata_field
            )

        form_object = DocumentConfigFormObject(
            document_mid=document_mid,
            document_title=document_title,
            document_uid=document_uid,
            document_version=document_version,
            document_classification=document_classification,
            document_requirement_prefix=document_requirement_prefix,
            document_custom_metadata_fields=document_custom_metadata_fields,
        )
        return form_object

    @staticmethod
    def create_from_document(
        *,
        document: SDocDocument,
    ) -> "DocumentConfigFormObject":
        assert isinstance(document, SDocDocument)

        document_custom_metadata_fields: List[DocumentMetadataFormField] = []
        for name, value in document.config.get_custom_metadata():
            document_custom_metadata_field = (
                DocumentMetadataFormField.create_from_document(
                    name=name, value=value
                )
            )
            document_custom_metadata_fields.append(
                document_custom_metadata_field
            )

        return DocumentConfigFormObject(
            document_mid=document.reserved_mid,
            document_title=document.title,
            document_uid=document.config.uid,
            document_version=document.config.version,
            document_classification=document.config.classification,
            document_requirement_prefix=document.config.requirement_prefix,
            document_custom_metadata_fields=document_custom_metadata_fields,
        )
