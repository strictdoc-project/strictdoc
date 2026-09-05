"""
Resolves a document's `IMPORT_FROM_FILE` grammar reference (an `@alias` or a
bare filename) to an actual path on disk.

This is a single source of truth for that resolution: it started out
inlined in `TraceabilityIndexBuilder.create()` (the read side, run once per
project build), and is reused by the grammar-editing save endpoints in
`strictdoc/server/routers/main_router.py` (the write side, so an edited
grammar is written back to the same file it was read from). Keeping both
sides calling the same function avoids them silently drifting apart.
"""

import os
import posixpath

from strictdoc.backend.sdoc.models.document import SDocDocument
from strictdoc.core.project_config import ProjectConfig


def resolve_grammar_file_relative_path(
    document: SDocDocument, project_config: ProjectConfig
) -> str:
    """
    Returns the project-root-relative, POSIX-style path to the `.sgra` file
    that `document.grammar.import_from_file` refers to: an `@alias` is
    looked up in `project_config.grammars`; a bare filename is resolved
    relative to the importing document's own directory.
    """

    assert document.grammar is not None
    assert document.grammar.import_from_file is not None
    assert document.meta is not None

    grammar_path = document.grammar.import_from_file
    if grammar_path.startswith("@"):
        grammar_path = project_config.grammars[grammar_path]
    else:
        grammar_path = posixpath.join(
            document.meta.input_doc_dir_rel_path.relative_path_posix,
            grammar_path,
        )
    return grammar_path


def resolve_grammar_file_full_path(
    document: SDocDocument, project_config: ProjectConfig
) -> str:
    """
    Same as resolve_grammar_file_relative_path(), joined with the project
    root so the result can be opened directly.
    """

    relative_path = resolve_grammar_file_relative_path(
        document, project_config
    )
    return os.path.join(project_config.get_project_root_path(), relative_path)
