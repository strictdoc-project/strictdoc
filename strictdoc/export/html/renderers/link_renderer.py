import re

from strictdoc.backend.dsl.models.document import Document
from strictdoc.backend.dsl.models.requirement import Requirement
from strictdoc.backend.dsl.models.section import Section
from strictdoc.core.finders.source_files_finder import SourceFile


class LinkRenderer:
    def __init__(self, output_html_root):
        self.output_html_root = output_html_root
        self.local_anchor_cache = {}
        self.req_link_cache = {}

    def render_local_anchor(self, node):
        if node in self.local_anchor_cache:
            return self.local_anchor_cache[node]
        if isinstance(node, Section):
            local_anchor = self._string_to_link(node.title)
        elif isinstance(node, Requirement):
            if node.uid and len(node.uid) > 0:
                local_anchor = self._string_to_link(node.uid)
            elif node.title and len(node.title) > 0:
                local_anchor = self._string_to_link(node.title)
            else:
                # TODO: This is not reliable
                local_anchor = str(id(node))
        else:
            raise NotImplementedError
        self.local_anchor_cache[node] = local_anchor
        return local_anchor

    def render_requirement_link(self, node, context_document, document_type):
        assert isinstance(node, Requirement)
        assert isinstance(context_document, Document)
        assert isinstance(document_type, str)
        local_link = self.render_local_anchor(node)
        if node.document == context_document:
            return f"#{local_link}"
        else:
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
            "document", source_file.level + 2
        )
        requirement_link = f"{document_link}#{local_link}"
        self.req_link_cache[link_cache_key][node] = requirement_link
        return requirement_link

    def render_source_file_link(
        self, requirement: Requirement, source_file_link: str
    ):
        document: Document = requirement.ng_document_reference.get_document()
        path_prefix = document.meta.get_root_path_prefix()
        source_file_link = f"{path_prefix}/_source_files/{document.meta.output_document_dir_rel_path}/{source_file_link}.html"
        return source_file_link

    def render_requirement_in_source_file_link(
        self,
        requirement: Requirement,
        source_link: str,
        context_source_file: SourceFile,
    ):
        assert isinstance(source_link, str)
        assert len(source_link) > 0

        def get_root_path_prefix(level):
            if level == 0:
                return ".."
            return ("../" * level)[:-1]

        path_prefix = get_root_path_prefix(context_source_file.level + 2)
        source_file_link = f"{path_prefix}/_source_files/{context_source_file.doctree_root_mount_path}/{source_link}.html#{requirement.uid}"
        return source_file_link

    def render_requirement_in_source_file_range_link(
        self,
        requirement: Requirement,
        source_link: str,
        context_source_file: SourceFile,
        range,
    ):
        assert isinstance(source_link, str)
        assert len(source_link) > 0

        def get_root_path_prefix(level):
            if level == 0:
                return ".."
            return ("../" * level)[:-1]

        path_prefix = get_root_path_prefix(context_source_file.level + 2)
        # source_file_link = f"{path_prefix}/_source_files/{context_source_file.doctree_root_mount_path}/{source_link}.html?begin={range.ng_source_line_begin}&end={range.ng_source_line_end}#{requirement.uid}"
        source_file_link = f"{path_prefix}/_source_files/{context_source_file.doctree_root_mount_path}/{source_link}.html#{requirement.uid}:{range.ng_source_line_begin}:{range.ng_source_line_end}"
        return source_file_link

    @staticmethod
    def _string_to_link(string):
        return re.sub(r"[^\w0-9]+", "-", string)
