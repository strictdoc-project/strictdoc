from typing import List, Optional

from strictdoc.backend.sdoc.models.grammar_element import (
    GrammarElementFieldMultipleChoice,
    GrammarElementFieldSingleChoice,
    GrammarElementFieldString,
    GrammarElementFieldTag,
    RequirementFieldType,
)
from strictdoc.export.html.form_objects.grammar_element_form_object import (
    GrammarElementFormObject,
    GrammarFormField,
    GrammarFormRelation,
)
from strictdoc.helpers.mid import MID


class _StubElement:
    def __init__(self, tag: str):
        self.tag = tag


class _StubGrammar:
    """
    A minimal stand-in for DocumentGrammar: convert_to_grammar_element()
    only ever calls get_element_by_mid(...).tag on it.
    """

    def __init__(self, tag: str):
        self._tag = tag

    def get_element_by_mid(self, _mid: str) -> _StubElement:
        return _StubElement(self._tag)


def _form_object(
    fields: List[GrammarFormField],
) -> GrammarElementFormObject:
    return GrammarElementFormObject(
        document_mid=MID.create(),
        element_mid=MID.create(),
        element_name="REQUIREMENT",
        is_composite=False,
        prefix="REQ-",
        view_style="Table",
        fields=fields,
        relations=[
            GrammarFormRelation(
                relation_mid=MID.create(),
                relation_type="Parent",
                relation_role="",
            )
        ],
        project_config=None,  # not used by validate()/convert_to_grammar_element()
        jinja_environment=None,  # not used by validate()/convert_to_grammar_element()
    )


def _custom_field(
    field_type: str,
    field_options: str = "",
    field_name: str = "TARGET_REVISION",
) -> GrammarFormField:
    return GrammarFormField(
        field_mid=MID.create(),
        field_name=field_name,
        field_human_title=None,
        field_required=True,
        reserved=False,
        field_type=field_type,
        field_options=field_options,
    )


def test_single_choice_field_survives_read_then_write_round_trip():
    grammar_field = GrammarElementFieldSingleChoice(
        parent=None,
        title="TARGET_REVISION",
        human_title=None,
        options=["C1", "C2"],
        required="True",
    )

    form_field = GrammarFormField.create_from_grammar_field(
        grammar_field=grammar_field
    )
    assert form_field.field_type == RequirementFieldType.SINGLE_CHOICE
    assert form_field.field_options == "C1, C2"

    converted = _form_object([form_field]).convert_to_grammar_element(
        _StubGrammar("REQUIREMENT")
    )

    converted_field = converted.fields[0]
    assert isinstance(converted_field, GrammarElementFieldSingleChoice)
    assert converted_field.options == ["C1", "C2"]


def test_multiple_choice_field_survives_read_then_write_round_trip():
    grammar_field = GrammarElementFieldMultipleChoice(
        parent=None,
        title="AFFECTED_MODULES",
        human_title=None,
        options=["Mechanics", "Electronics"],
        required="False",
    )

    form_field = GrammarFormField.create_from_grammar_field(
        grammar_field=grammar_field
    )
    assert form_field.field_type == RequirementFieldType.MULTIPLE_CHOICE
    assert form_field.field_options == "Mechanics, Electronics"

    converted = _form_object([form_field]).convert_to_grammar_element(
        _StubGrammar("REQUIREMENT")
    )

    converted_field = converted.fields[0]
    assert isinstance(converted_field, GrammarElementFieldMultipleChoice)
    assert converted_field.options == ["Mechanics", "Electronics"]


def test_string_and_tag_fields_carry_no_options():
    string_field = GrammarFormField.create_from_grammar_field(
        grammar_field=GrammarElementFieldString(
            parent=None, title="NOTE", human_title=None, required="False"
        )
    )
    tag_field = GrammarFormField.create_from_grammar_field(
        grammar_field=GrammarElementFieldTag(
            parent=None, title="TAGS", human_title=None, required="False"
        )
    )

    assert string_field.field_type == RequirementFieldType.STRING
    assert string_field.field_options == ""
    assert tag_field.field_type == RequirementFieldType.TAG
    assert tag_field.field_options == ""


def test_saving_a_string_field_unchanged_still_produces_a_string_field():
    # Regression test for the data-loss bug this change fixes: previously
    # convert_to_grammar_element() rebuilt every field as a plain String,
    # so a SingleChoice field saved via this form would silently lose its
    # type and options. A String field must still round-trip as a String.
    form_field = _custom_field(RequirementFieldType.STRING, field_name="NOTE")

    converted = _form_object([form_field]).convert_to_grammar_element(
        _StubGrammar("REQUIREMENT")
    )

    assert isinstance(converted.fields[0], GrammarElementFieldString)


def test_changing_a_string_field_to_single_choice_produces_a_choice_field():
    form_field = _custom_field(
        RequirementFieldType.SINGLE_CHOICE, field_options="C1, C2, D1"
    )

    converted = _form_object([form_field]).convert_to_grammar_element(
        _StubGrammar("REQUIREMENT")
    )

    converted_field = converted.fields[0]
    assert isinstance(converted_field, GrammarElementFieldSingleChoice)
    assert converted_field.options == ["C1", "C2", "D1"]


def test_option_list_ignores_extra_whitespace_and_trailing_commas():
    form_field = _custom_field(
        RequirementFieldType.SINGLE_CHOICE, field_options=" C1 ,C2,  , D1,"
    )

    converted = _form_object([form_field]).convert_to_grammar_element(
        _StubGrammar("REQUIREMENT")
    )

    assert converted.fields[0].options == ["C1", "C2", "D1"]


def test_empty_options_on_a_single_choice_field_fails_validation():
    form_field = _custom_field(RequirementFieldType.SINGLE_CHOICE)

    form_object = _form_object([form_field])

    assert form_object.validate() is False
    assert (
        len(form_object.get_errors(form_field.get_input_field_options())) == 1
    )


def test_empty_options_on_a_multiple_choice_field_fails_validation():
    form_field = _custom_field(RequirementFieldType.MULTIPLE_CHOICE)

    form_object = _form_object([form_field])

    assert form_object.validate() is False
    assert (
        len(form_object.get_errors(form_field.get_input_field_options())) == 1
    )


def test_empty_options_on_a_string_field_is_not_an_error():
    form_field = _custom_field(RequirementFieldType.STRING, field_name="NOTE")

    form_object = _form_object([form_field])

    assert form_object.validate() is True
