import collections

from strictdoc.backend.dsl.models.document import Document
from strictdoc.backend.dsl.models.requirement import (
    CompositeRequirement,
    Requirement,
)
from strictdoc.backend.dsl.models.section import FreeText, Section
from strictdoc.core.level_counter import LevelCounter


class DocumentCachingIterator:
    def __init__(self, document):
        assert isinstance(document, Document)

        self.document = document
        self.nodes_cache = []
        self.toc_nodes_cache = []

    def table_of_contents(self):
        if len(self.toc_nodes_cache) > 0:
            yield from self.toc_nodes_cache
            return

        for node in self.all_content():
            if isinstance(node, FreeText):
                continue

            self.toc_nodes_cache.append(node)
            yield node

    def all_content(self):
        if len(self.nodes_cache) > 0:
            yield from self.nodes_cache
            return

        document = self.document
        level_counter = LevelCounter()

        task_list = collections.deque(document.section_contents)

        while True:
            if not task_list:
                break

            current = task_list.popleft()

            if (
                isinstance(current, Section)
                or isinstance(current, CompositeRequirement)
                or isinstance(current, Requirement)
            ):
                assert current.ng_level, f"Node has no ng_level: {current}"
                level_counter.adjust(current.ng_level)

                current.context.title_number_string = level_counter.get_string()

            self.nodes_cache.append(current)
            yield current

            if isinstance(current, Section):
                task_list.extendleft(reversed(current.section_contents))

            if isinstance(current, CompositeRequirement):
                task_list.extendleft(reversed(current.requirements))
