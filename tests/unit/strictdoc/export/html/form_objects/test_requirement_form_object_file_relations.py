import pytest
from starlette.datastructures import FormData

from strictdoc.core.project_config import ProjectConfig, ProjectFeature
from strictdoc.export.html.form_objects.requirement_form_object import (
    RequirementFormObject,
    RequirementReferenceFormField,
)
from tests.unit.helpers.document_builder import DocumentBuilder


class _FileIndexStub:
    def __init__(self, paths):
        self.paths = paths

    def get_coverage_info_weak(self, path):
        return object() if path in self.paths else None


class _TraceabilityIndexStub:
    def __init__(self, paths):
        self.file_index = _FileIndexStub(paths)

    def get_file_traceability_index(self):
        return self.file_index


def _config(enabled: bool = True) -> ProjectConfig:
    config = ProjectConfig.default_config()
    if enabled:
        config.project_features.append(
            ProjectFeature.REQUIREMENT_TO_SOURCE_TRACEABILITY
        )
    return config


def _field(path: str, line_range: str = "") -> RequirementReferenceFormField:
    return RequirementReferenceFormField(
        field_mid="mid",
        field_type=RequirementReferenceFormField.FieldType.FILE,
        field_value=path,
        field_role=None,
        field_line_range=line_range,
    )


def _validate(field, enabled=True):
    RequirementFormObject._validate_file_relation(
        field, _TraceabilityIndexStub({"src/file.c"}), _config(enabled)
    )
    return field.validation_messages


def test_valid_path_and_line_range_is_normalized():
    field = _field("src/file.c", " 3 ,7 ")
    assert _validate(field) == []
    assert field.field_line_range == "3, 7"


def test_valid_path_without_line_range():
    assert _validate(_field("src/file.c")) == []


def test_unknown_path_is_rejected():
    messages = _validate(_field("src/missing.c"))
    assert len(messages) == 1
    assert "does not exist" in messages[0]


def test_empty_path_is_rejected():
    assert _validate(_field("")) == ["File path must not be empty."]


@pytest.mark.parametrize("line_range", ["1", "a, b", "1, 2, 3", "1-2"])
def test_malformed_line_range_is_rejected(line_range):
    messages = _validate(_field("src/file.c", line_range))
    assert len(messages) == 1
    assert "format" in messages[0]


@pytest.mark.parametrize("line_range", ["5, 4", "0, 4"])
def test_out_of_order_line_range_is_rejected(line_range):
    messages = _validate(_field("src/file.c", line_range))
    assert len(messages) == 1
    assert "not greater" in messages[0]


def test_feature_disabled_explains_itself():
    messages = _validate(_field("src/file.c"), enabled=False)
    assert len(messages) == 1
    assert "REQUIREMENT_TO_SOURCE_TRACEABILITY" in messages[0]


def test_create_from_request_reads_file_relation_with_line_range():
    document_builder = DocumentBuilder()
    document_builder.add_requirement("REQ-001")
    document = document_builder.build()
    form_data = FormData(
        [
            ("context_document_mid", document.reserved_mid),
            ("revision", "0"),
            ("element_type", "REQUIREMENT"),
            ("requirement[fields][f1][name]", "UID"),
            ("requirement[fields][f1][value]", "REQ-001"),
            ("requirement[relations][r1][typerole]", "File"),
            ("requirement[relations][r1][value]", " src/file.c "),
            ("requirement[relations][r1][line_range]", "1, 2"),
            ("requirement[relations][r1][is_new]", "true"),
            # A new, empty File row is discarded like an empty Parent row.
            ("requirement[relations][r2][typerole]", "File"),
            ("requirement[relations][r2][value]", ""),
            ("requirement[relations][r2][is_new]", "true"),
        ]
    )
    form_object = RequirementFormObject.create_from_request(
        is_new=False,
        requirement_mid="req_mid",
        request_form_data=form_data,
        document=document,
        existing_requirement_uid="REQ-001",
    )
    assert len(form_object.reference_fields) == 1
    field = form_object.reference_fields[0]
    assert field.field_type == "File"
    assert field.field_value == "src/file.c"
    assert field.field_line_range == "1, 2"
