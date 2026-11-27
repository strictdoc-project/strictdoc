"""
@relation(SDOC-SRS-48, scope=file)

DocumentFinder reads the documents and grammars that have an up-to-date
cache entry in the main process. Only the other files go to the
parallelizer.
"""

from pathlib import Path
from typing import Any, Callable, Iterable, List, Optional

from strictdoc.core.document_tree import DocumentTree
from strictdoc.core.file_system.document_finder import DocumentFinder
from strictdoc.core.project_config import ProjectConfig
from strictdoc.helpers.parallelizer import NullParallelizer

SDOC_TEMPLATE = """\
[DOCUMENT]
TITLE: {title}

[REQUIREMENT]
UID: REQ-{index}
STATEMENT: Requirement {index}.
"""

MARKDOWN_DOCUMENT = """\
# Markdown document

## Markdown requirement

**UID**: REQ-MD

**Statement**: The Markdown requirement.
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


class RecordingParallelizer(NullParallelizer):
    """Records how many files each call sends to the parallelizer."""

    def __init__(self) -> None:
        self.task_counts: List[int] = []

    def run_parallel(
        self,
        contents: List[Any],
        processing_func: Callable[[Any], Any],
        on_item_complete: Optional[Callable[[int, Any], None]] = None,
    ) -> Iterable[Any]:
        self.task_counts.append(len(contents))
        return super().run_parallel(contents, processing_func, on_item_complete)


def create_project(tmp_path: Path) -> ProjectConfig:
    input_root = tmp_path / "input"
    input_root.mkdir()
    for index_ in range(1, 7):
        (input_root / f"doc_{index_}.sdoc").write_text(
            SDOC_TEMPLATE.format(title=f"Document {index_}", index=index_)
        )
    (input_root / "markdown.md").write_text(MARKDOWN_DOCUMENT)
    (input_root / "grammar.sgra").write_text(GRAMMAR)

    project_config = ProjectConfig.default_config()
    project_config.input_paths = [str(input_root)]
    project_config.output_dir = str(tmp_path / "output")
    project_config.export_output_html_root = str(tmp_path / "output" / "html")
    project_config.dir_for_sdoc_cache = str(tmp_path / "cache")
    return project_config


def find_documents(
    project_config: ProjectConfig,
) -> tuple[DocumentTree, List[int]]:
    parallelizer = RecordingParallelizer()
    document_tree, _ = DocumentFinder.find_sdoc_content(
        project_config, parallelizer
    )
    return document_tree, parallelizer.task_counts


def get_titles(document_tree: DocumentTree) -> List[str]:
    return [str(document_.title) for document_ in document_tree.document_list]


def test_01_cold_run_sends_all_files_to_the_parallelizer(
    tmp_path: Path,
) -> None:
    project_config = create_project(tmp_path)

    document_tree, task_counts = find_documents(project_config)

    # 6 SDoc documents, 1 Markdown document, and 1 grammar.
    assert task_counts == [8]
    assert len(document_tree.document_list) == 7
    assert len(document_tree.map_grammars_by_filenames) == 1


def test_02_hot_run_reads_all_files_from_the_cache(tmp_path: Path) -> None:
    project_config = create_project(tmp_path)
    cold_document_tree, _ = find_documents(project_config)

    hot_document_tree, task_counts = find_documents(project_config)

    assert task_counts == [0]
    assert get_titles(hot_document_tree) == get_titles(cold_document_tree)
    assert len(hot_document_tree.map_grammars_by_filenames) == 1


def test_03_changed_file_is_parsed_and_keeps_its_position(
    tmp_path: Path,
) -> None:
    project_config = create_project(tmp_path)
    cold_document_tree, _ = find_documents(project_config)
    (tmp_path / "input" / "doc_3.sdoc").write_text(
        SDOC_TEMPLATE.format(title="Changed document 3", index=3)
    )

    document_tree, task_counts = find_documents(project_config)

    assert task_counts == [1]
    assert get_titles(document_tree) == [
        "Changed document 3" if title_ == "Document 3" else title_
        for title_ in get_titles(cold_document_tree)
    ]
