import re

from strictdoc.backend.dsl.models import Section, Requirement


class LinkRenderer:

    def render(self, node):
        if isinstance(node, Section):
            return self._string_to_link(node.title)
        if isinstance(node, Requirement):
            if node.title and len(node.title) > 0:
                return self._string_to_link(node.title)
            if node.uid and len(node.uid) > 0:
                return self._string_to_link(node.uid)
            return ""
        raise NotImplementedError

    @staticmethod
    def _string_to_link(string):
        return re.sub(r'[^A-Za-z0-9]+', '-', string)
