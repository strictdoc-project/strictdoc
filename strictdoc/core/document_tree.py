from typing import Dict, List

from strictdoc.backend.sdoc.models.document import Document


class DocumentTree:
    def __init__(
        self, file_tree, document_list, map_docs_by_paths, map_docs_by_rel_paths
    ):
        assert isinstance(file_tree, list)
        assert isinstance(document_list, list)
        assert isinstance(map_docs_by_paths, dict)
        assert isinstance(map_docs_by_rel_paths, dict)
        self.file_tree = file_tree
        self.document_list: List[Document] = document_list
        self.map_docs_by_paths = map_docs_by_paths
        self.map_docs_by_rel_paths: Dict[str, Document] = map_docs_by_rel_paths
        self.source_tree = None  # attached later.

    def __repr__(self):
        return (
            f"DocumentTree("
            f"{self.file_tree}"
            f", "
            f"document_list: {self.document_list}"
            f")"
        )

    def get_document_by_path(self, doc_full_path):
        document = self.map_docs_by_paths[doc_full_path]
        return document

    def get_document_by_rel_path(self, doc_rel_path):
        document = self.map_docs_by_rel_paths[doc_rel_path]
        return document

    def attach_source_tree(self, source_tree):
        self.source_tree = source_tree
