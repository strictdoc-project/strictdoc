import re

from strictdoc.backend.dsl.models.document import Document
from strictdoc.backend.dsl.models.requirement import Requirement
from strictdoc.backend.dsl.models.section import Section


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

    @staticmethod
    def _string_to_link(string):
        return re.sub(r"[^\w0-9]+", "-", string)
