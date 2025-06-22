from dataclasses import dataclass
from typing import Iterator, Tuple, Union

from strictdoc.backend.sdoc.models.document import SDocDocument
from strictdoc.backend.sdoc.models.document_from_file import DocumentFromFile
from strictdoc.backend.sdoc.models.model import (
    SDocDocumentFromFileIF,
    SDocDocumentIF,
    SDocElementIF,
    SDocNodeIF,
    SDocSectionIF,
)
from strictdoc.backend.sdoc.models.node import (
    SDocNode,
)
from strictdoc.backend.sdoc.models.section import SDocSection
from strictdoc.helpers.cast import assert_cast


@dataclass
class DocumentIterationContext:
    node: SDocElementIF
    level_stack: Tuple[int, ...]
    custom_level: bool = False

    def get_level(self) -> int:
        return len(self.level_stack)

    def get_level_string(self) -> str:
        if (
            isinstance(self.node, SDocNode)
            and self.node.node_type == "TEXT"
            and self.node.reserved_title is None
        ):
            return ""

        if self.node.ng_resolved_custom_level == "None":
            return ""

        if self.node.ng_resolved_custom_level is not None:
            return self.node.ng_resolved_custom_level

        if self.custom_level:
            return ""

        return ".".join(map(str, self.level_stack))


class DocumentCachingIterator:
    def __init__(self, document: SDocDocument) -> None:
        assert isinstance(document, SDocDocument), document

        self.document: SDocDocument = document

    def table_of_contents(
        self,
    ) -> Iterator[Tuple[SDocElementIF, DocumentIterationContext]]:
        for node_, context_ in self.all_content(
            print_fragments=True,
        ):
            if isinstance(node_, SDocNode):
                if node_.reserved_title is None:
                    continue
                if (
                    not self.document.config.is_requirement_in_toc()
                    and node_.node_type != "SECTION"
                ):
                    continue
            yield node_, context_

    def all_content(
        self,
        print_fragments: bool = False,
    ) -> Iterator[Tuple[SDocElementIF, DocumentIterationContext]]:
        root_node = self.document

        yield from self.all_node_content(
            root_node,
            print_fragments=print_fragments,
            level_stack=(),
            custom_level=not root_node.config.auto_levels,
        )

    def all_node_content(
        self,
        node: Union[SDocElementIF, DocumentFromFile],
        print_fragments: bool = False,
        level_stack: Tuple[int, ...] = (),
        custom_level: bool = False,
    ) -> Iterator[Tuple[SDocElementIF, DocumentIterationContext]]:
        if isinstance(node, SDocSection):
            # If node is not whitelisted, we ignore it. Also, note that due to
            # this early return, all child nodes of this node are ignored
            # as well because they are not added to the iteration queue.
            if not node.ng_whitelisted:
                return

            # FIXME: This will be changed to yield only context.
            context = DocumentIterationContext(
                node, level_stack, custom_level=custom_level
            )
            node.context.title_number_string = context.get_level_string()
            node.ng_level = context.get_level()

            yield node, context

            current_number = 0
            for subnode_ in node.section_contents:
                if subnode_.ng_resolved_custom_level is None and not (
                    isinstance(subnode_, SDocNode)
                    and subnode_.node_type == "TEXT"
                    and subnode_.reserved_title is None
                ):
                    current_number += 1

                yield from self.all_node_content(
                    assert_cast(
                        subnode_,
                        (
                            SDocNodeIF,
                            SDocSectionIF,
                            SDocDocumentIF,
                            SDocDocumentFromFileIF,
                        ),
                    ),
                    print_fragments=print_fragments,
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

            # FIXME: This will be changed to yield only context.
            context = DocumentIterationContext(
                node, level_stack, custom_level=custom_level
            )
            node.context.title_number_string = context.get_level_string()
            node.ng_level = context.get_level()

            yield node, context

            current_number = 0
            if node.section_contents is not None:
                for subnode_ in node.section_contents:
                    if subnode_.ng_resolved_custom_level is None and not (
                        isinstance(subnode_, SDocNode)
                        and subnode_.node_type == "TEXT"
                    ):
                        current_number += 1

                    yield from self.all_node_content(
                        subnode_,
                        print_fragments=print_fragments,
                        level_stack=level_stack + (current_number,),
                        custom_level=custom_level
                        or subnode_.ng_resolved_custom_level is not None,
                    )

        elif isinstance(node, SDocDocument):
            if (
                print_fragments
                and node.document_is_included()
                and self.document != node
            ):
                context = DocumentIterationContext(
                    node, level_stack, custom_level=custom_level
                )
                node.context.title_number_string = context.get_level_string()
                node.ng_level = context.get_level()

                yield node, context

            current_number = 0
            for subnode_ in node.section_contents:
                if subnode_.ng_resolved_custom_level is None and not (
                    isinstance(subnode_, SDocNode)
                    and subnode_.node_type == "TEXT"
                ):
                    current_number += 1
                yield from self.all_node_content(
                    assert_cast(
                        subnode_,
                        (
                            SDocNodeIF,
                            SDocSectionIF,
                            SDocDocumentIF,
                            SDocDocumentFromFileIF,
                        ),
                    ),
                    print_fragments=print_fragments,
                    level_stack=level_stack + (current_number,),
                    custom_level=custom_level
                    or subnode_.ng_resolved_custom_level is not None,
                )

        elif isinstance(node, DocumentFromFile):
            if not print_fragments:
                return

            assert node.resolved_document is not None

            yield from self.all_node_content(
                node.resolved_document,
                print_fragments=print_fragments,
                level_stack=level_stack,
            )

        else:
            raise NotImplementedError
