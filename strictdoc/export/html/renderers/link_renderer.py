import re

from strictdoc.backend.dsl.models.requirement import Requirement
from strictdoc.backend.dsl.models.section import Section


class LinkRenderer:

    def __init__(self, output_html_root):
        self.output_html_root = output_html_root

    def render(self, node):
        if isinstance(node, Section):
            return self._string_to_link(node.title)
        if isinstance(node, Requirement):
            if node.title and len(node.title) > 0:
                return self._string_to_link(node.title)
            if node.uid and len(node.uid) > 0:
                return self._string_to_link(node.uid)

            # TODO: This is not reliable
            return str(id(node))
        raise NotImplementedError

    @staticmethod
    def _string_to_link(string):
        return re.sub(r'[^\w0-9]+', '-', string)
