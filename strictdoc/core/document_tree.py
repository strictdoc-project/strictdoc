# mypy: disable-error-code="no-untyped-def"
from typing import Dict, List, Optional

from strictdoc.backend.sdoc.models.document import SDocDocument
from strictdoc.backend.sdoc.models.document_grammar import DocumentGrammar
from strictdoc.core.source_tree import SourceTree


class DocumentTree:
    def __init__(
        self,
        file_tree,
        document_list,
        map_docs_by_paths: Dict[str, SDocDocument],
        map_docs_by_rel_paths,
        map_grammars_by_filenames: Dict[str, DocumentGrammar],
    ):
        assert isinstance(file_tree, list)
        assert isinstance(document_list, list)
        assert isinstance(map_docs_by_paths, dict)
        assert isinstance(map_docs_by_rel_paths, dict)
        self.file_tree = file_tree
        self.document_list: List[SDocDocument] = document_list
        self.map_docs_by_paths: Dict[str, SDocDocument] = map_docs_by_paths
        self.map_docs_by_rel_paths: Dict[str, SDocDocument] = (
            map_docs_by_rel_paths
        )
        self.map_grammars_by_filenames: Dict[str, DocumentGrammar] = (
            map_grammars_by_filenames
        )

        self.source_tree: Optional[SourceTree] = None  # Attached later.

    def __repr__(self):
        return (
            f"DocumentTree("
            f"{self.file_tree}"
            f", "
            f"document_list: {self.document_list}"
            f")"
        )

    def get_document_by_path(self, doc_full_path: str) -> SDocDocument:
        document = self.map_docs_by_paths[doc_full_path]
        return document

    def get_document_by_rel_path(self, doc_rel_path: str) -> SDocDocument:
        assert isinstance(doc_rel_path, str), doc_rel_path
        document = self.map_docs_by_rel_paths[doc_rel_path]
        return document

    def get_grammar_by_filename(
        self, filename: str
    ) -> Optional[DocumentGrammar]:
        return self.map_grammars_by_filenames.get(filename)

    def attach_source_tree(self, source_tree: SourceTree):
        self.source_tree = source_tree
