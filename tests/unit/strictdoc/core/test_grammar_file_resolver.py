import os

from strictdoc.core.grammar_file_resolver import (
    resolve_grammar_file_full_path,
    resolve_grammar_file_relative_path,
)
from strictdoc.helpers.paths import SDocRelativePath
from tests.unit.helpers.document_builder import DocumentBuilder


def test_alias_resolves_via_project_config_grammars():
    builder = DocumentBuilder()
    document = builder.build()
    document.grammar.import_from_file = "@my_grammar"
    builder.project_config.grammars = {"@my_grammar": "sub/my_grammar.sgra"}
    builder.project_config.input_paths = ["/project/root"]

    assert (
        resolve_grammar_file_relative_path(document, builder.project_config)
        == "sub/my_grammar.sgra"
    )
    assert resolve_grammar_file_full_path(
        document, builder.project_config
    ) == os.path.join("/project/root", "sub/my_grammar.sgra")


def test_bare_filename_resolves_relative_to_document_directory():
    builder = DocumentBuilder()
    document = builder.build()
    document.grammar.import_from_file = "grammar.sgra"
    document.meta.input_doc_dir_rel_path = SDocRelativePath("eurobot")
    builder.project_config.input_paths = ["/project/root"]

    assert (
        resolve_grammar_file_relative_path(document, builder.project_config)
        == "eurobot/grammar.sgra"
    )
    assert resolve_grammar_file_full_path(
        document, builder.project_config
    ) == os.path.join("/project/root", "eurobot/grammar.sgra")


def test_bare_filename_at_project_root_has_no_leading_slash():
    builder = DocumentBuilder()
    document = builder.build()
    document.grammar.import_from_file = "grammar.sgra"
    # DocumentBuilder's document already sits at the project root
    # (input_doc_dir_rel_path == "").
    builder.project_config.input_paths = ["/project/root"]

    assert (
        resolve_grammar_file_relative_path(document, builder.project_config)
        == "grammar.sgra"
    )
