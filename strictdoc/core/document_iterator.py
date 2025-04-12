# mypy: disable-error-code="attr-defined"
from typing import Iterator, Tuple, Union

from strictdoc.backend.sdoc.models.document import SDocDocument
from strictdoc.backend.sdoc.models.document_from_file import DocumentFromFile
from strictdoc.backend.sdoc.models.model import (
    SDocCompositeNodeIF,
    SDocDocumentFromFileIF,
    SDocDocumentIF,
    SDocElementIF,
    SDocNodeIF,
    SDocSectionIF,
)
from strictdoc.backend.sdoc.models.node import (
    SDocCompositeNode,
    SDocNode,
)
from strictdoc.backend.sdoc.models.section import SDocSection
from strictdoc.helpers.cast import assert_cast


class DocumentCachingIterator:
    def __init__(self, document: SDocDocument) -> None:
        assert isinstance(document, SDocDocument), document

        self.document: SDocDocument = document

    def table_of_contents(self) -> Iterator[SDocElementIF]:
        nodes_to_skip = (
            (SDocNode,)
            if not self.document.config.is_requirement_in_toc()
            else ()
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
    ) -> Iterator[SDocElementIF]:
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
        node: Union[SDocElementIF, DocumentFromFile],
        print_fragments: bool = False,
        print_fragments_from_files: bool = False,
        level_stack: Tuple[int, ...] = (),
        custom_level: bool = False,
    ) -> Iterator[SDocElementIF]:
        def get_level_string_(
            node_: Union[SDocSection, SDocNode, SDocCompositeNode],
        ) -> str:
            if (
                isinstance(node_, SDocNode)
                and node_.node_type == "TEXT"
                and node_.reserved_title is None
            ):
                return ""

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
                if subnode_.ng_resolved_custom_level is None and not (
                    isinstance(subnode_, SDocNode)
                    and subnode_.node_type == "TEXT"
                    and subnode_.reserved_title is None
                ):
                    current_number += 1

                yield from self._all_content(
                    assert_cast(
                        subnode_,
                        (
                            SDocNodeIF,
                            SDocCompositeNodeIF,
                            SDocSectionIF,
                            SDocDocumentIF,
                            SDocDocumentFromFileIF,
                        ),
                    ),
                    print_fragments=print_fragments,
                    print_fragments_from_files=print_fragments_from_files,
                    level_stack=level_stack + (current_number,),
                    custom_level=custom_level
                    or subnode_.ng_resolved_custom_level is not None,
                )

        elif isinstance(node, SDocCompositeNode):
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
            if node.requirements is not None:
                for subnode_ in node.requirements:
                    if subnode_.ng_resolved_custom_level is None and not (
                        isinstance(subnode_, SDocNode)
                        and subnode_.node_type == "TEXT"
                    ):
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
            if (
                print_fragments
                and node.document_is_included()
                and self.document != node
            ):
                node.context.title_number_string = ".".join(
                    map(str, level_stack)
                )
                node.ng_level = len(level_stack)

                yield node

            current_number = 0
            for subnode_ in node.section_contents:
                if subnode_.ng_resolved_custom_level is None and not (
                    isinstance(subnode_, SDocNode)
                    and subnode_.node_type == "TEXT"
                ):
                    current_number += 1
                yield from self._all_content(
                    assert_cast(
                        subnode_,
                        (
                            SDocNodeIF,
                            SDocCompositeNodeIF,
                            SDocSectionIF,
                            SDocDocumentIF,
                            SDocDocumentFromFileIF,
                        ),
                    ),
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

            assert node.resolved_document is not None

            yield from self._all_content(
                node.resolved_document,
                print_fragments=print_fragments,
                print_fragments_from_files=print_fragments_from_files,
                level_stack=level_stack,
            )

        else:
            raise NotImplementedError
