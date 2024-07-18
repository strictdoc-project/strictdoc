# mypy: disable-error-code="arg-type,no-untyped-call,no-untyped-def,type-arg"
from collections import defaultdict
from typing import Dict

from starlette.datastructures import FormData

from strictdoc.backend.sdoc.models.section import SDocSection
from strictdoc.export.html.form_objects.requirement_form_object import (
    RequirementFormField,
    RequirementFormFieldType,
)
from strictdoc.helpers.auto_described import auto_described
from strictdoc.helpers.cast import assert_cast
from strictdoc.helpers.form_data import parse_form_data
from strictdoc.helpers.mid import MID
from strictdoc.helpers.string import sanitize_html_form_field
from strictdoc.server.error_object import ErrorObject


@auto_described
class SectionFormObject(ErrorObject):
    def __init__(
        self,
        *,
        section_mid: str,
        section_uid_field: RequirementFormField,
        section_title_field: RequirementFormField,
        context_document_mid: str,
    ):
        assert isinstance(section_mid, str)
        assert isinstance(section_uid_field, RequirementFormField)
        assert isinstance(section_title_field, RequirementFormField)
        assert isinstance(context_document_mid, str)

        super().__init__()
        self.section_mid: str = section_mid
        self.section_uid_field: RequirementFormField = section_uid_field
        self.section_title_field: RequirementFormField = section_title_field
        self.context_document_mid = context_document_mid

    @property
    def section_uid(self):
        return self.section_uid_field.field_value

    @property
    def section_title(self):
        return self.section_title_field.field_value

    @staticmethod
    def create_new(context_document_mid: str):
        return SectionFormObject(
            section_mid=MID.create(),
            section_uid_field=RequirementFormField(
                field_mid=MID.create(),
                field_name="UID",
                field_type=RequirementFormFieldType.SINGLELINE,
                field_value="",
            ),
            section_title_field=RequirementFormField(
                field_mid=MID.create(),
                field_name="TITLE",
                field_type=RequirementFormFieldType.SINGLELINE,
                field_value="",
            ),
            context_document_mid=context_document_mid,
        )

    @staticmethod
    def create_from_section(*, section: SDocSection, context_document_mid: str):
        uid_field_value = (
            section.reserved_uid if section.reserved_uid is not None else ""
        )
        title_field_value = section.title if section.title is not None else ""

        return SectionFormObject(
            section_mid=section.reserved_mid,
            section_uid_field=RequirementFormField(
                field_mid=MID.create(),
                field_name="UID",
                field_type=RequirementFormFieldType.SINGLELINE,
                field_value=uid_field_value,
            ),
            section_title_field=RequirementFormField(
                field_mid=MID.create(),
                field_name="TITLE",
                field_type=RequirementFormFieldType.SINGLELINE,
                field_value=title_field_value,
            ),
            context_document_mid=context_document_mid,
        )

    @staticmethod
    def create_from_request(
        *,
        section_mid: str,
        request_form_data: FormData,
    ) -> "SectionFormObject":
        request_form_data_as_list = [
            (field_name, field_value)
            for field_name, field_value in request_form_data.multi_items()
        ]
        request_form_dict: Dict = assert_cast(
            parse_form_data(request_form_data_as_list), dict
        )
        context_document_mid = request_form_dict["context_document_mid"]
        requirement_dict = request_form_dict["requirement"]
        requirement_fields_dict = requirement_dict["fields"]

        requirement_fields = defaultdict(list)
        for _, field_dict in requirement_fields_dict.items():
            field_name = field_dict["name"]
            field_value = field_dict["value"]
            requirement_fields[field_name].append(field_value)

        uid_field_value = requirement_fields["UID"][0]
        sanitized_uid_field_value: str = sanitize_html_form_field(
            uid_field_value, multiline=False
        )
        section_uid_field = RequirementFormField(
            field_mid=MID.create(),
            field_name="UID",
            field_type=RequirementFormFieldType.SINGLELINE,
            field_value=sanitized_uid_field_value,
        )

        title_field_value = requirement_fields["TITLE"][0]
        sanitized_title_field_value: str = sanitize_html_form_field(
            title_field_value, multiline=False
        )
        section_title_field = RequirementFormField(
            field_mid=MID.create(),
            field_name="TITLE",
            field_type=RequirementFormFieldType.SINGLELINE,
            field_value=sanitized_title_field_value,
        )

        form_object = SectionFormObject(
            section_mid=section_mid,
            section_uid_field=section_uid_field,
            section_title_field=section_title_field,
            context_document_mid=context_document_mid,
        )
        return form_object
