from typing import Optional, Tuple

from strictdoc.backend.sdoc.models.document import SDocDocument
from strictdoc.backend.sdoc.models.document_from_file import DocumentFromFile
from strictdoc.backend.sdoc.models.node import (
    CompositeRequirement,
    SDocNode,
)
from strictdoc.backend.sdoc.models.section import FreeText, SDocSection


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

        yield from self._all_content(
            root_node,
            print_fragments=print_fragments,
            print_fragments_from_files=print_fragments_from_files,
            level_stack=(),
            custom_level=not root_node.config.auto_levels,
        )

    def _all_content(
        self,
        node,
        print_fragments: bool = False,
        print_fragments_from_files: bool = False,
        level_stack: Optional[Tuple] = (),
        custom_level: bool = False,
    ):
        def get_level_string_(node_) -> str:
            if node_.ng_resolved_custom_level == "None":
                return ""

            if node_.ng_resolved_custom_level is not None:
                return node_.ng_resolved_custom_level

            if custom_level:
                return ""

            return ".".join(map(str, level_stack))

        if isinstance(node, SDocSection):
            # If node is not whitelisted, we ignore it. Also, note that due to
            # this early return, all child nodes of this node are ignored
            # as well because they are not added to the iteration queue.
            if not node.ng_whitelisted:
                return

            # FIXME: This will be changed.
            node.context.title_number_string = get_level_string_(node)
            node.ng_level = len(level_stack)

            yield node

            current_number = 0
            for subnode_ in node.section_contents:
                if subnode_.ng_resolved_custom_level is None:
                    current_number += 1

                yield from self._all_content(
                    subnode_,
                    print_fragments=print_fragments,
                    print_fragments_from_files=print_fragments_from_files,
                    level_stack=level_stack + (current_number,),
                    custom_level=custom_level
                    or subnode_.ng_resolved_custom_level is not None,
                )

        elif isinstance(node, CompositeRequirement):
            # If node is not whitelisted, we ignore it. Also, note that due to
            # this early return, all child nodes of this node are ignored
            # as well because they are not added to the iteration queue.
            if not node.ng_whitelisted:
                return

            # FIXME: This will be changed.
            node.context.title_number_string = get_level_string_(node)
            node.ng_level = len(level_stack)

            yield node

            current_number = 0
            for subnode_ in node.requirements:
                if subnode_.ng_resolved_custom_level is None:
                    current_number += 1

                yield from self._all_content(
                    subnode_,
                    print_fragments=print_fragments,
                    print_fragments_from_files=print_fragments_from_files,
                    level_stack=level_stack + (current_number,),
                    custom_level=custom_level
                    or subnode_.ng_resolved_custom_level is not None,
                )

        elif isinstance(node, SDocNode):
            # If node is not whitelisted, we ignore it. Also, note that due to
            # this early return, all child nodes of this node are ignored
            # as well because they are not added to the iteration queue.
            if not node.ng_whitelisted:
                return

            # FIXME: This will be changed.
            node.context.title_number_string = get_level_string_(node)
            node.ng_level = len(level_stack)

            yield node

        elif isinstance(node, SDocDocument):
            current_number = 0
            for subnode_ in node.section_contents:
                if subnode_.ng_resolved_custom_level is None:
                    current_number += 1
                yield from self._all_content(
                    subnode_,
                    print_fragments=print_fragments,
                    print_fragments_from_files=print_fragments_from_files,
                    level_stack=level_stack + (current_number,),
                    custom_level=custom_level
                    or subnode_.ng_resolved_custom_level is not None,
                )

        elif isinstance(node, DocumentFromFile):
            if not print_fragments:
                if print_fragments_from_files:
                    yield node
                return

            yield from self._all_content(
                node.top_section,
                print_fragments=print_fragments,
                print_fragments_from_files=print_fragments_from_files,
                level_stack=level_stack,
            )

        else:
            raise NotImplementedError
