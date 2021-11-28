from strictdoc.export.html.document_type import DocumentType


class DocumentMeta:
    def __init__(  # pylint: disable=too-many-arguments
        self,
        level,
        file_tree_mount_folder,
        document_filename_base,
        input_doc_full_path,
        input_doc_dir_rel_path,
        output_document_dir_full_path,
        output_document_dir_rel_path,
    ):
        self.level = level
        self.file_tree_mount_folder = file_tree_mount_folder
        self.document_filename_base = document_filename_base
        self.input_doc_full_path = input_doc_full_path
        self.input_doc_rel_path = input_doc_dir_rel_path
        self.output_document_dir_full_path = output_document_dir_full_path
        self.output_document_dir_rel_path = output_document_dir_rel_path

    # Paths
    def get_html_doc_path(self):
        return (
            f"{self.output_document_dir_full_path}"
            f"/"
            f"{self.document_filename_base}.html"
        )

    def get_html_doc_standalone_path(self):
        return (
            f"{self.output_document_dir_full_path}"
            f"/"
            f"{self.document_filename_base}.standalone.html"
        )

    def get_html_table_path(self):
        return (
            f"{self.output_document_dir_full_path}"
            f"/"
            f"{self.document_filename_base}-TABLE.html"
        )

    def get_html_traceability_path(self):
        return (
            f"{self.output_document_dir_full_path}"
            f"/"
            f"{self.document_filename_base}-TRACE.html"
        )

    def get_html_deep_traceability_path(self):
        return (
            f"{self.output_document_dir_full_path}"
            f"/"
            f"{self.document_filename_base}-DEEP-TRACE.html"
        )

    # Links
    def get_html_doc_link(self):
        return (
            f"{self.output_document_dir_rel_path}"
            f"/"
            f"{self.document_filename_base}.html"
        )

    def get_html_table_link(self):
        return (
            f"{self.output_document_dir_rel_path}"
            f"/"
            f"{self.document_filename_base}-TABLE.html"
        )

    def get_html_traceability_link(self):
        return (
            f"{self.output_document_dir_rel_path}"
            f"/"
            f"{self.document_filename_base}-TRACE.html"
        )

    def get_html_deep_traceability_link(self):
        return (
            f"{self.output_document_dir_rel_path}"
            f"/"
            f"{self.document_filename_base}-DEEP-TRACE.html"
        )

    def get_html_link(self, document_type: DocumentType, other_doc_level):
        assert isinstance(document_type, DocumentType)

        document_type_type = document_type.document_type
        path_prefix = self.get_root_path_prefix(other_doc_level)
        if document_type_type == DocumentType.DOCUMENT:
            document_link = self.get_html_doc_link()
        elif document_type_type == DocumentType.TABLE:
            document_link = self.get_html_table_link()
        elif document_type_type == DocumentType.TRACE:
            document_link = self.get_html_traceability_link()
        elif document_type_type == DocumentType.DEEPTRACE:
            document_link = self.get_html_deep_traceability_link()
        else:
            raise NotImplementedError
        return f"{path_prefix}/{document_link}"

    def get_root_path_prefix(self, other_doc_level=None):
        level = self.level if not other_doc_level else other_doc_level
        if level == 0:
            return ".."
        return ("../" * level)[:-1]
