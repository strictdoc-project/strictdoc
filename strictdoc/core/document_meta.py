# mypy: disable-error-code="no-untyped-call,no-untyped-def"
from typing import Optional

from strictdoc.export.html.document_type import DocumentType
from strictdoc.helpers.auto_described import auto_described
from strictdoc.helpers.paths import SDocRelativePath


@auto_described
class DocumentMeta:
    def __init__(
        self,
        level: int,
        file_tree_mount_folder,
        document_filename: str,
        document_filename_base,
        input_doc_full_path,
        input_doc_rel_path: SDocRelativePath,
        input_doc_dir_rel_path: SDocRelativePath,
        input_doc_assets_dir_rel_path: SDocRelativePath,
        output_document_dir_full_path,
        output_document_dir_rel_path: SDocRelativePath,
    ):
        """
        Example explaining meta data stored by this class:

        DocumentMeta(
            level = 1,
            file_tree_mount_folder = "doc_project",
            document_filename = "sample.sdoc",
            document_filename_base = "sample",
            input_doc_full_path = "/tmp/doc_project/child.sdoc",
            input_doc_rel_path = "child.sdoc",
            input_doc_dir_rel_path = "",
            input_doc_assets_dir_rel_path = "doc_project/_assets",
            output_document_dir_full_path = "/tmp/doc_project/output/html/doc_project",
            output_document_dir_rel_path = "doc_project"
        )
        """
        assert isinstance(
            input_doc_rel_path, SDocRelativePath
        ), input_doc_rel_path
        assert isinstance(
            input_doc_dir_rel_path, SDocRelativePath
        ), input_doc_dir_rel_path
        assert isinstance(
            input_doc_assets_dir_rel_path, SDocRelativePath
        ), input_doc_assets_dir_rel_path
        assert isinstance(
            output_document_dir_rel_path, SDocRelativePath
        ), output_document_dir_rel_path

        self.level: int = level
        self.file_tree_mount_folder = file_tree_mount_folder
        self.document_filename: str = document_filename
        self.document_filename_base = document_filename_base
        self.input_doc_full_path = input_doc_full_path
        self.input_doc_rel_path: SDocRelativePath = input_doc_rel_path
        self.input_doc_dir_rel_path: SDocRelativePath = input_doc_dir_rel_path
        self.input_doc_assets_dir_rel_path: SDocRelativePath = (
            input_doc_assets_dir_rel_path
        )
        self.output_document_dir_full_path = output_document_dir_full_path
        self.output_document_dir_rel_path: SDocRelativePath = (
            output_document_dir_rel_path
        )

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

    def get_html_pdf_path(self):
        return (
            f"{self.output_document_dir_full_path}"
            f"/"
            f"{self.document_filename_base}-PDF.html"
        )

    # Links
    def get_html_doc_link(self) -> str:
        file_name_part = f"{self.document_filename_base}.html"
        if len(self.output_document_dir_rel_path.relative_path_posix) == 0:
            return file_name_part
        return (
            f"{self.output_document_dir_rel_path.relative_path_posix}"
            "/"
            f"{file_name_part}"
        )

    def get_html_table_link(self) -> str:
        file_name_part = f"{self.document_filename_base}-TABLE.html"
        if len(self.output_document_dir_rel_path.relative_path_posix) == 0:
            return file_name_part
        return (
            f"{self.output_document_dir_rel_path.relative_path_posix}"
            "/"
            f"{file_name_part}"
        )

    def get_html_traceability_link(self) -> str:
        file_name_part = f"{self.document_filename_base}-TRACE.html"
        if len(self.output_document_dir_rel_path.relative_path_posix) == 0:
            return file_name_part
        return (
            f"{self.output_document_dir_rel_path.relative_path_posix}"
            "/"
            f"{file_name_part}"
        )

    def get_html_deep_traceability_link(self) -> str:
        file_name_part = f"{self.document_filename_base}-DEEP-TRACE.html"
        if len(self.output_document_dir_rel_path.relative_path_posix) == 0:
            return file_name_part
        return (
            f"{self.output_document_dir_rel_path.relative_path_posix}"
            "/"
            f"{file_name_part}"
        )

    def get_html_pdf_link(self) -> str:
        file_name_part = f"{self.document_filename_base}-PDF.html"
        if len(self.output_document_dir_rel_path.relative_path_posix) == 0:
            return file_name_part
        return (
            f"{self.output_document_dir_rel_path.relative_path_posix}"
            "/"
            f"{file_name_part}"
        )

    def get_html_standalone_document_link(self) -> str:
        return (
            f"{self.output_document_dir_rel_path.relative_path_posix}"
            f"/"
            f"{self.document_filename_base}.standalone.html"
        )

    def get_html_link(
        self,
        document_type: DocumentType,
        other_doc_level: Optional[int],
    ) -> str:
        assert isinstance(document_type, DocumentType)

        document_type_type = document_type.document_type
        path_prefix: str = self.get_root_path_prefix(other_doc_level)
        if document_type_type == DocumentType.DOCUMENT:
            document_link = self.get_html_doc_link()
        elif document_type_type == DocumentType.TABLE:
            document_link = self.get_html_table_link()
        elif document_type_type == DocumentType.TRACE:
            document_link = self.get_html_traceability_link()
        elif document_type_type == DocumentType.DEEPTRACE:
            document_link = self.get_html_deep_traceability_link()
        elif document_type_type == DocumentType.PDF:
            document_link = self.get_html_pdf_link()
        else:
            raise NotImplementedError
        # We reach here the document is a bundle document.
        if len(path_prefix) == 0:
            return document_link
        return f"{path_prefix}/{document_link}"

    def get_root_path_prefix(self, other_doc_level=None) -> str:
        level: int = self.level if not other_doc_level else other_doc_level
        if level == 0:
            return ""
        return ("../" * level)[:-1]  # mypy: disable=no-any-return
