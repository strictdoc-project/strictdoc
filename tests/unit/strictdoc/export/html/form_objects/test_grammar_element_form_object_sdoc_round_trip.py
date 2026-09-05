"""
End-to-end (parse -> form -> render -> write) coverage for the grammar
element editor's field-type/choice-options editing, using the real .sdoc
reader/writer and the real Jinja templates instead of hand-built model
objects, since that's what test_grammar_element_form_object.py's plain-object
tests cannot exercise: whether an existing SingleChoice field (e.g.
TARGET_REVISION: C1/C2) survives being read into the form, rendered by the
actual row_with_custom_field template, and written back out unchanged, and
whether a mentor-added option shows up in both places after saving.
"""

from datetime import datetime

from strictdoc.backend.sdoc.models.grammar_element import RequirementFieldType
from strictdoc.backend.sdoc.reader import SDReader
from strictdoc.backend.sdoc.writer import SDWriter
from strictdoc.export.html.form_objects.grammar_element_form_object import (
    GrammarElementFormObject,
)
from strictdoc.export.html.html_templates import HTMLTemplates

INPUT_SDOC = """\
[DOCUMENT]
TITLE: Doc

[GRAMMAR]
ELEMENTS:
- TAG: REQUIREMENT
  FIELDS:
  - TITLE: UID
    TYPE: String
    REQUIRED: False
  - TITLE: TITLE
    TYPE: String
    REQUIRED: False
  - TITLE: STATEMENT
    TYPE: String
    REQUIRED: False
  - TITLE: TARGET_REVISION
    TYPE: SingleChoice(C1, C2)
    REQUIRED: True
  RELATIONS:
  - TYPE: Parent

[REQUIREMENT]
TITLE: Req
STATEMENT: Statement
TARGET_REVISION: C1
"""


def test_untouched_save_preserves_the_single_choice_field_and_its_options(
    default_project_config,
):
    # Regression test for the bug this change fixes: saving the grammar
    # element editor used to always rebuild every field as a plain String,
    # so even a no-op save would have turned TARGET_REVISION into a String
    # field and silently dropped its C1/C2 options.
    document = SDReader().read(INPUT_SDOC)
    element = document.grammar.elements_by_type["REQUIREMENT"]

    form_object = GrammarElementFormObject.create_from_document(
        document=document,
        element_mid=element.mid,
        project_config=default_project_config,
        jinja_environment=None,
    )

    assert form_object.validate() is True

    updated_element = form_object.convert_to_grammar_element(document.grammar)
    document.grammar.update_element(element, updated_element)

    output = SDWriter(default_project_config).write(document)

    assert "TYPE: SingleChoice(C1, C2)" in output
    assert "TARGET_REVISION: C1" in output


def test_appending_a_new_revision_via_the_form_shows_up_in_the_written_sdoc(
    default_project_config,
):
    document = SDReader().read(INPUT_SDOC)
    element = document.grammar.elements_by_type["REQUIREMENT"]

    form_object = GrammarElementFormObject.create_from_document(
        document=document,
        element_mid=element.mid,
        project_config=default_project_config,
        jinja_environment=None,
    )

    target_revision_field = next(
        field_
        for field_ in form_object.fields
        if field_.field_name == "TARGET_REVISION"
    )
    assert target_revision_field.field_type == (
        RequirementFieldType.SINGLE_CHOICE
    )
    assert target_revision_field.field_options == "C1, C2"

    # Simulate a mentor appending a new revision from the UI.
    target_revision_field.field_options = "C1, C2, D1"

    assert form_object.validate() is True

    updated_element = form_object.convert_to_grammar_element(document.grammar)
    document.grammar.update_element(element, updated_element)

    output = SDWriter(default_project_config).write(document)

    assert "TYPE: SingleChoice(C1, C2, D1)" in output
    # The existing REQUIREMENT's own value is untouched by this save.
    assert "TARGET_REVISION: C1" in output


def test_the_actual_template_renders_the_field_type_and_options(
    default_project_config,
):
    # Exercises the real Jinja template
    # (row_with_custom_field/index.jinja), not just the Python model, so a
    # template syntax error or a wrong data-testid would fail this test.
    html_templates = HTMLTemplates.create(
        project_config=default_project_config,
        enable_caching=False,
        strictdoc_last_update=datetime.today(),
    )

    document = SDReader().read(INPUT_SDOC)
    element = document.grammar.elements_by_type["REQUIREMENT"]

    form_object = GrammarElementFormObject.create_from_document(
        document=document,
        element_mid=element.mid,
        project_config=default_project_config,
        jinja_environment=html_templates.jinja_environment(),
    )

    target_revision_field = next(
        field_
        for field_ in form_object.fields
        if field_.field_name == "TARGET_REVISION"
    )

    rendered = form_object.render_row_with_custom_field(target_revision_field)

    assert 'data-testid="select-field-type"' in rendered
    assert '<option\n          value="SingleChoice"\n          selected' in (
        rendered
    )
    assert 'data-testid="form-field-custom_field_options"' in rendered
    assert ">C1, C2</sdoc-contenteditable>" in rendered
