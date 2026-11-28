"""
SDReader and SDocGrammarReader build their textX metamodels on the first
parse. A read from the cache does not build a metamodel.
"""

from pathlib import Path
from typing import Any, List, Union

import pytest
from textx.metamodel import TextXMetaModel

from strictdoc.backend.sdoc import grammar_reader as grammar_reader_module
from strictdoc.backend.sdoc import reader as reader_module
from strictdoc.backend.sdoc.grammar_reader import SDocGrammarReader
from strictdoc.backend.sdoc.reader import SDReader
from strictdoc.core.project_config import ProjectConfig

SDOC_DOCUMENT = """\
[DOCUMENT]
TITLE: Document {index}

[REQUIREMENT]
UID: REQ-{index}
STATEMENT: Requirement {index}.
"""

GRAMMAR = """\
[GRAMMAR]
ELEMENTS:
- TAG: TEXT
  FIELDS:
  - TITLE: STATEMENT
    TYPE: String
    REQUIRED: True
"""

ReaderClass = Union[type[SDReader], type[SDocGrammarReader]]


def count_built_meta_models(
    monkeypatch: pytest.MonkeyPatch, module: Any, reader_class: ReaderClass
) -> List[TextXMetaModel]:
    """
    Start the test with no shared metamodel and record each metamodel that
    the reader builds.
    """
    built_meta_models: List[TextXMetaModel] = []
    metamodel_from_str = module.metamodel_from_str

    def metamodel_from_str_(*args: Any, **kwargs: Any) -> TextXMetaModel:
        meta_model = metamodel_from_str(*args, **kwargs)
        built_meta_models.append(meta_model)
        return meta_model

    monkeypatch.setattr(module, "metamodel_from_str", metamodel_from_str_)
    monkeypatch.setattr(reader_class, "_meta_model", None)
    return built_meta_models


def create_project_config(tmp_path: Path) -> ProjectConfig:
    project_config = ProjectConfig.default_config()
    project_config.output_dir = str(tmp_path / "output")
    project_config.dir_for_sdoc_cache = str(tmp_path / "cache")
    return project_config


def test_01_sdoc_readers_share_one_meta_model_built_on_first_parse(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    built_meta_models = count_built_meta_models(
        monkeypatch, reader_module, SDReader
    )

    document_1 = SDReader.read(SDOC_DOCUMENT.format(index=1))
    document_2 = SDReader().read(SDOC_DOCUMENT.format(index=2))

    assert len(built_meta_models) == 1
    assert document_1.title == "Document 1"
    assert document_2.title == "Document 2"


def test_02_sdoc_read_from_cache_does_not_build_a_meta_model(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    project_config = create_project_config(tmp_path)
    input_file = tmp_path / "document.sdoc"
    input_file.write_text(SDOC_DOCUMENT.format(index=1))
    # Parse the file once to create its cache entry.
    SDReader().read_from_file(str(input_file), project_config)
    built_meta_models = count_built_meta_models(
        monkeypatch, reader_module, SDReader
    )

    document = SDReader().read_from_file(str(input_file), project_config)

    assert built_meta_models == []
    assert document.title == "Document 1"


def test_03_grammar_readers_share_one_meta_model_built_on_first_parse(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    built_meta_models = count_built_meta_models(
        monkeypatch, grammar_reader_module, SDocGrammarReader
    )

    grammar_1 = SDocGrammarReader.read(GRAMMAR)
    grammar_2 = SDocGrammarReader.read(GRAMMAR)

    assert len(built_meta_models) == 1
    assert grammar_1.elements[0].tag == "TEXT"
    assert grammar_2.elements[0].tag == "TEXT"


def test_04_grammar_read_from_cache_does_not_build_a_meta_model(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    project_config = create_project_config(tmp_path)
    input_file = tmp_path / "grammar.sgra"
    input_file.write_text(GRAMMAR)
    # Parse the file once to create its cache entry.
    SDocGrammarReader().read_from_file(str(input_file), project_config)
    built_meta_models = count_built_meta_models(
        monkeypatch, grammar_reader_module, SDocGrammarReader
    )

    grammar = SDocGrammarReader().read_from_file(
        str(input_file), project_config
    )

    assert built_meta_models == []
    assert grammar.elements[0].tag == "TEXT"
