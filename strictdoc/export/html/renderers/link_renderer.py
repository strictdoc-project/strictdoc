import re
from typing import Optional

from strictdoc.backend.sdoc.models.document import Document
from strictdoc.backend.sdoc.models.reference import FileReference
from strictdoc.backend.sdoc.models.requirement import Requirement
from strictdoc.backend.sdoc.models.section import Section
from strictdoc.core.finders.source_files_finder import SourceFile
from strictdoc.export.html.document_type import DocumentType


class LinkRenderer:
    def __init__(self, *, root_path, static_path: str):
        assert isinstance(root_path, str)
        assert isinstance(static_path, str), static_path
        assert len(static_path) > 0, static_path

        self.root_path: str = root_path
        self.static_path: str = (
            f"{root_path}/{static_path}"
            if len(root_path) > 0
            else f"{static_path}"
        )
        self.local_anchor_cache = {}
        self.req_link_cache = {}

    def render_url(self, url):
        if len(self.root_path) == 0:
            return url
        return self.root_path + "/" + url

    def render_static_url(self, url):
        static_url = self.static_path + "/" + url
        return static_url

    # This rarely used helper adds slashes to the import statements within
    # <script type="module">, for example project_index/index.jinja.
    # Otherwise, scripts are not imported correctly.
    def render_static_url_with_prefix(self, url):
        static_url = "/" + self.static_path + "/" + url
        return static_url

    def render_local_anchor(self, node):
        if node in self.local_anchor_cache:
            return self.local_anchor_cache[node]
        unique_prefix = node.context.title_number_string
        if isinstance(node, Section):
            local_anchor = f"{unique_prefix}-{self._string_to_link(node.title)}"
        elif isinstance(node, Requirement):
            if node.reserved_uid and len(node.reserved_uid) > 0:
                local_anchor = (
                    f"{unique_prefix}-{self._string_to_link(node.reserved_uid)}"
                )
            elif (
                node.reserved_title is not None and len(node.reserved_title) > 0
            ):
                local_anchor = (
                    f"{unique_prefix}-"
                    f"{self._string_to_link(node.reserved_title)}"
                )
            else:
                # TODO: This is not reliable
                local_anchor = str(id(node))
        else:
            raise NotImplementedError
        self.local_anchor_cache[node] = local_anchor
        return local_anchor

    def render_requirement_link(
        self,
        node,
        context_document: Optional[Document],
        document_type: DocumentType,
    ):
        assert isinstance(node, (Requirement, Section)), node
        assert isinstance(context_document, Document), context_document
        assert isinstance(document_type, DocumentType), document_type
        local_link = self.render_local_anchor(node)
        if context_document and node.document == context_document:
            return f"#{local_link}"

        link_cache_key = (document_type, context_document.meta.level)
        if link_cache_key in self.req_link_cache:
            document_type_cache = self.req_link_cache[link_cache_key]
            if node in document_type_cache:
                return document_type_cache[node]
        else:
            self.req_link_cache[link_cache_key] = {}
        document_link = node.document.meta.get_html_link(
            document_type, context_document.meta.level
        )
        requirement_link = f"{document_link}#{local_link}"
        self.req_link_cache[link_cache_key][node] = requirement_link
        return requirement_link

    def render_requirement_link_from_source_file(self, node, source_file):
        assert isinstance(node, Requirement)
        assert isinstance(source_file, SourceFile)
        local_link = self.render_local_anchor(node)
        link_cache_key = ("document", source_file.level)
        if link_cache_key in self.req_link_cache:
            document_type_cache = self.req_link_cache[link_cache_key]
            if node in document_type_cache:
                return document_type_cache[node]
        else:
            self.req_link_cache[link_cache_key] = {}
        document_link = node.document.meta.get_html_link(
            DocumentType.document(), source_file.level + 1
        )
        requirement_link = f"{document_link}#{local_link}"
        self.req_link_cache[link_cache_key][node] = requirement_link
        return requirement_link

    @staticmethod
    def render_source_file_link(
        requirement: Requirement, file_reference: FileReference
    ):
        assert isinstance(file_reference, FileReference), file_reference

        document_or_none: Optional[
            Document
        ] = requirement.ng_document_reference.get_document()
        assert document_or_none is not None
        document: Document = document_or_none
        path_prefix = document.meta.get_root_path_prefix()
        source_file_link = (
            f"{path_prefix}"
            "/"
            f"_source_files"
            "/"
            f"{file_reference.get_posix_path()}.html"
        )
        return source_file_link

    @staticmethod
    def render_source_file_link_from_root(file_reference: FileReference):
        assert isinstance(file_reference, FileReference)
        return f"_source_files/{file_reference.get_posix_path()}.html"

    @staticmethod
    def render_source_file_link_from_root_2(source_file: SourceFile):
        assert isinstance(source_file, SourceFile)
        source_file_link = (
            "_source_files"
            "/"
            f"{source_file.in_doctree_source_file_rel_path_posix}.html"
        )
        return source_file_link

    @staticmethod
    def render_requirement_in_source_file_link(
        requirement: Requirement,
        source_link: FileReference,
        context_source_file: SourceFile,
    ):
        def get_root_path_prefix(level):
            if level == 0:
                return ".."
            return ("../" * level)[:-1]

        path_prefix = get_root_path_prefix(context_source_file.level + 1)
        source_file_link = (
            f"{path_prefix}"
            f"/_source_files"
            f"/{source_link.get_posix_path()}.html"
            f"#{requirement.reserved_uid}"
        )
        return source_file_link

    @staticmethod
    def render_requirement_in_source_file_range_link_using_id(
        req_uid: str,
        source_link: str,
        context_source_file: SourceFile,
        source_range,
    ):
        assert isinstance(source_link, str)
        assert isinstance(context_source_file, SourceFile)
        assert len(source_link) > 0

        def get_root_path_prefix(level):
            if level == 0:
                return ".."
            return ("../" * level)[:-1]

        path_prefix = get_root_path_prefix(context_source_file.level + 1)
        source_file_link = (
            f"{path_prefix}"
            f"/_source_files"
            f"/{source_link}.html"
            f"#{req_uid}"
            f"#{source_range.ng_range_line_begin}"
            f"#{source_range.ng_range_line_end}"
        )
        return source_file_link

    def render_requirement_in_source_file_range_link(
        self,
        requirement: Requirement,
        source_link: FileReference,
        context_source_file: SourceFile,
        source_range,
    ):
        assert isinstance(source_link, FileReference)
        assert isinstance(context_source_file, SourceFile)
        return self.render_requirement_in_source_file_range_link_using_id(
            requirement.reserved_uid,
            source_link.get_posix_path(),
            context_source_file,
            source_range,
        )

    @staticmethod
    def _string_to_link(string):
        return re.sub(r"[^\w0-9]+", "-", string)
