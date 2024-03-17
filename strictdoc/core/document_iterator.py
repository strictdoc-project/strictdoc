import collections
from typing import List, Tuple

from strictdoc.backend.sdoc.models.document import SDocDocument
from strictdoc.backend.sdoc.models.document_from_file import FragmentFromFile
from strictdoc.backend.sdoc.models.node import (
    CompositeRequirement,
    SDocNode,
)
from strictdoc.backend.sdoc.models.section import FreeText, SDocSection
from strictdoc.core.level_counter import LevelCounter


class DocumentCachingIterator:
    def __init__(self, document):
        assert isinstance(document, SDocDocument)

        self.document = document

    def table_of_contents(self):
        nodes_to_skip = (
            (FreeText, SDocNode)
            if not self.document.config.is_requirement_in_toc()
            else FreeText
        )

        for node in self.all_content(
            print_fragments=True,
            print_fragments_from_files=False,
        ):
            if isinstance(node, nodes_to_skip):
                continue
            if isinstance(node, SDocNode) and node.reserved_title is None:
                continue
            yield node

    def all_content(
        self,
        print_fragments: bool = False,
        print_fragments_from_files: bool = False,
    ):
        root_node = self.document

        level_counter = LevelCounter()

        root_contents: List[Tuple] = []

        for node_ in root_node.section_contents:
            root_contents.append((node_, 1))

        task_list = collections.deque(root_contents)

        while True:
            if not task_list:
                break

            current, current_level = task_list.popleft()
            # FIXME
            current.ng_level = current_level

            if isinstance(current, FragmentFromFile):
                if not print_fragments:
                    if print_fragments_from_files:
                        yield current
                else:
                    assert current.resolved_document is not None
                    section_contents = map(
                        lambda node_: (node_, current_level),
                        reversed(current.section_contents),
                    )

                    task_list.extendleft(section_contents)
                continue

            # If node is not whitelisted, we ignore it. Also, note that due to
            # this early return, all child nodes of this node are ignored
            # as well because they are not added to the iteration queue.
            if not current.ng_whitelisted:
                continue

            if isinstance(
                current, (SDocSection, SDocNode, CompositeRequirement)
            ):
                assert current.ng_level, f"Node has no ng_level: {current}"

                if current.ng_resolved_custom_level != "None":
                    level_counter.adjust(current_level)

                    # FIXME: Remove the need to do branching here.
                    current.context.title_number_string = (
                        current.ng_resolved_custom_level
                        if current.ng_resolved_custom_level
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

            yield current

            if isinstance(current, SDocSection):
                section_contents = map(
                    lambda node_: (node_, current_level + 1),
                    reversed(current.section_contents),
                )
                task_list.extendleft(section_contents)

            elif isinstance(current, CompositeRequirement):
                section_contents = map(
                    lambda node_: (node_, current_level + 1),
                    reversed(current.requirements),
                )
                task_list.extendleft(section_contents)

    @staticmethod
    def specific_node_with_normal_levels(node):
        if isinstance(node, SDocSection):
            initial_content = node.section_contents
        elif isinstance(node, CompositeRequirement):
            initial_content = node.requirements
        else:
            return

        task_list = collections.deque(initial_content)

        while True:
            if not task_list:
                break

            current = task_list.popleft()

            if isinstance(
                current, (SDocSection, SDocNode, CompositeRequirement)
            ):
                # We are not interested in the nodes without level in this
                # iterator.
                if current.ng_resolved_custom_level == "None":
                    continue

            yield current

            if isinstance(current, SDocSection):
                task_list.extendleft(reversed(current.section_contents))

            elif isinstance(current, CompositeRequirement):
                task_list.extendleft(reversed(current.requirements))
