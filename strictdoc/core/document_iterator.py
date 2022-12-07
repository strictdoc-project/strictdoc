import collections

from strictdoc.backend.sdoc.models.document import Document
from strictdoc.backend.sdoc.models.requirement import (
    CompositeRequirement,
    Requirement,
)
from strictdoc.backend.sdoc.models.section import FreeText, Section
from strictdoc.core.level_counter import LevelCounter


class DocumentCachingIterator:
    def __init__(self, document):
        assert isinstance(document, Document)

        self.document = document
        self.nodes_cache = []
        self.toc_nodes_cache = []

    def invalidate_cache(self):
        self.nodes_cache.clear()
        self.toc_nodes_cache.clear()

    def table_of_contents(self):
        # TODO: WIP
        # if len(self.toc_nodes_cache) > 0:
        #     yield from self.toc_nodes_cache
        #     return

        nodes_to_skip = (
            (FreeText, Requirement)
            if not self.document.config.is_requirement_in_toc()
            else FreeText
        )

        for node in self.all_content():
            if isinstance(node, nodes_to_skip):
                continue
            if isinstance(node, Requirement) and node.title is None:
                continue
            self.toc_nodes_cache.append(node)
            yield node

    def all_content(self):
        # TODO: WIP
        # if len(self.nodes_cache) > 0:
        #     yield from self.nodes_cache
        #     return

        document = self.document
        level_counter = LevelCounter()

        task_list = collections.deque(document.section_contents)

        while True:
            if not task_list:
                break

            current = task_list.popleft()

            if isinstance(
                current, (Section, Requirement, CompositeRequirement)
            ):
                assert current.ng_level, f"Node has no ng_level: {current}"

                if current.level != "None":
                    level_counter.adjust(current.ng_level)
                    # TODO: Remove the need to do branching here.
                    current.context.title_number_string = (
                        current.level
                        if current.level
                        else level_counter.get_string()
                    )
                else:
                    # The idea is to include a section header without affecting
                    # the level of the nested elements (i.e. requirements), but
                    # keeping the section title in a dedicated row in DOC, TBL
                    # and TR/DTR views.
                    # Such an option can be very useful when dealing with source
                    # requirements documents with inconsistent sectioning (such
                    # as some technical standards/normative), that need to be
                    # included in a custom project.
                    # https://github.com/strictdoc-project/strictdoc/issues/639
                    current.context.title_number_string = ""

            self.nodes_cache.append(current)
            yield current

            if isinstance(current, Section):
                task_list.extendleft(reversed(current.section_contents))

            elif isinstance(current, CompositeRequirement):
                task_list.extendleft(reversed(current.requirements))
