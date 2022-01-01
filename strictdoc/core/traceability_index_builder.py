import sys

from strictdoc.backend.sdoc.models.inline_link import InlineLink
from strictdoc.backend.sdoc.models.requirement import Requirement
from strictdoc.core.document_iterator import DocumentCachingIterator
from strictdoc.core.document_tree import DocumentTree
from strictdoc.core.error_message import ErrorMessage
from strictdoc.core.traceability_index import (
    TraceabilityIndex,
    FileTraceabilityIndex,
)
from strictdoc.core.tree_cycle_detector import TreeCycleDetector
from strictdoc.helpers.timing import timing_decorator


class TraceabilityIndexBuilder:
    @staticmethod
    @timing_decorator("Collect traceability information")
    def create(document_tree: DocumentTree):
        requirements_map = {}
        requirements_children_map = {}
        tags_map = {}
        document_iterators = {}
        file_traceability_index = FileTraceabilityIndex()

        # It seems to be impossible to accomplish everything in just one for
        # loop. One particular problem that requires two passes: it is not
        # possible to know after one iteration if any of the requirements
        # reference parents that do not exist.
        #
        # Step #1:
        # - Collect a dictionary of all requirements in the document tree:
        # {req_id: req}
        # - Each requirement's 'parents_uids' is populated with the forward
        # declarations of its parents uids.
        # - A separate map is created: {req_id: [req_children]}
        # At this point some information is in place but it was not known if
        # some of the UIDs could not be resolved which is the task of the second
        # step.
        #
        # Step #2:
        # - Check if each requirement's has valid parent links.
        # - Resolve parent forward declarations
        # - Re-assign children declarations
        # - Detect cycles
        # - Calculate depth of both parent and child links.
        for document in document_tree.document_list:
            document_iterator = DocumentCachingIterator(document)
            document_iterators[document] = document_iterator
            if document.name not in tags_map:
                tags_map[document.name] = {}
            for node in document_iterator.all_content():
                if not node.uid:
                    continue
                if node.uid in requirements_map:
                    other_req_doc = requirements_map[node.uid]["document"]
                    if other_req_doc == document:
                        print(
                            "error: DocumentIndex: "
                            "two nodes with the same UID "
                            "exist in the same document: "
                            f'{node.uid} in "{document.title}".'
                        )
                    else:
                        print(
                            "error: DocumentIndex: "
                            "two nodes with the same UID "
                            "exist in two different documents: "
                            f'{node.uid} in "{document.title}" and '
                            f'"{other_req_doc.title}".'
                        )
                    sys.exit(1)
                requirements_map[node.uid] = {
                    "document": document,
                    "requirement": node,
                    "parents": [],
                    "parents_uids": [],
                    "children": [],
                }
                if not node.is_requirement:
                    continue
                requirement: Requirement = node
                document_tags = tags_map[document.name]
                if requirement.tags is not None:
                    for tag in requirement.tags:
                        if tag not in document_tags:
                            document_tags[tag] = 0
                        document_tags[tag] += 1
                if requirement.uid not in requirements_children_map:
                    requirements_children_map[requirement.uid] = []
                for ref in requirement.references:
                    if ref.ref_type == "File":
                        file_traceability_index.register(requirement)
                        continue
                    if ref.ref_type != "Parent":
                        continue
                    requirements_map[requirement.uid]["parents_uids"].append(
                        ref.path
                    )
                    if ref.path not in requirements_children_map:
                        requirements_children_map[ref.path] = []
                    requirements_children_map[ref.path].append(requirement)

        # Now iterate over the requirements again to build an in-depth map of
        # parents and children.
        parents_cycle_detector = TreeCycleDetector(requirements_map)
        children_cycle_detector = TreeCycleDetector(requirements_map)

        requirements_child_depth_map = {}
        requirements_parent_depth_map = {}
        documents_ref_depth_map = {}
        document_parents_map = {}
        document_children_map = {}

        for document in document_tree.document_list:
            document_parents_map.setdefault(document, set())
            document_children_map.setdefault(document, set())
            document_iterator = document_iterators[document]
            max_parent_depth, max_child_depth = 0, 0

            for node in document_iterator.all_content():
                if node.is_section:
                    for free_text in node.free_texts:
                        for part in free_text.parts:
                            if isinstance(part, InlineLink):
                                if part.link not in requirements_map:
                                    print(
                                        ErrorMessage.inline_link_uid_not_exist(
                                            part.link
                                        )
                                    )
                                    sys.exit(1)
                if not node.is_requirement:
                    continue
                requirement: Requirement = node
                if not requirement.uid:
                    continue

                # Now it is possible to resolve parents first checking if they
                # indeed exist.
                requirement_parent_ids = requirements_map[requirement.uid][
                    "parents_uids"
                ]
                for requirement_parent_id in requirement_parent_ids:
                    if requirement_parent_id not in requirements_map:
                        # TODO: Strict variant of the behavior will be to stop
                        # and raise an error message.
                        print(
                            f"warning: [DocumentIndex.create] "
                            f"Requirement {requirement.uid} references "
                            f"parent requirement which doesn't exist: "
                            f"{requirement_parent_id}"
                        )
                        requirements_children_map.pop(
                            requirement_parent_id, None
                        )
                        continue
                    parent_requirement = requirements_map[
                        requirement_parent_id
                    ]["requirement"]
                    requirements_map[requirement.uid]["parents"].append(
                        parent_requirement
                    )
                    # Set document dependencies.
                    parent_document = requirements_map[requirement_parent_id][
                        "document"
                    ]
                    document_parents_map.setdefault(requirement.document, set())
                    document_parents_map[requirement.document].add(
                        parent_document
                    )
                    document_children_map.setdefault(parent_document, set())
                    document_children_map[parent_document].add(
                        requirement.document
                    )

                # [SDOC-VALIDATION-NO-CYCLES]
                # Detect cycles
                parents_cycle_detector.check_node(
                    requirement.uid,
                    lambda requirement_id: requirements_map[requirement_id][
                        "parents_uids"
                    ],
                )
                children_cycle_detector.check_node(
                    requirement.uid,
                    lambda requirement_id: list(
                        map(
                            lambda current_requirement: current_requirement.uid,
                            requirements_children_map[requirement_id],
                        )
                    ),
                )
                # [/SDOC-VALIDATION-NO-CYCLES]

                if requirement.uid not in requirements_child_depth_map:
                    child_depth = 0
                    requirements_map[requirement.uid][
                        "children"
                    ] = requirements_children_map[requirement.uid]
                    queue = requirements_children_map[requirement.uid]
                    while True:
                        if len(queue) == 0:
                            break
                        child_depth += 1
                        deeper_queue = []
                        for child in queue:
                            deeper_queue.extend(
                                requirements_children_map[child.uid]
                            )
                        queue = deeper_queue
                    requirements_child_depth_map[requirement.uid] = child_depth
                    max_child_depth = max(max_child_depth, child_depth)

                # Calculate parent depth
                if requirement.uid not in requirements_parent_depth_map:
                    parent_depth = 0
                    queue = requirement_parent_ids
                    while True:
                        if len(queue) == 0:
                            break
                        parent_depth += 1
                        deeper_queue = []
                        for parent_uid in queue:
                            if parent_uid not in requirements_map:
                                continue
                            deeper_queue.extend(
                                requirements_map[parent_uid]["parents_uids"]
                            )
                        queue = deeper_queue
                    requirements_parent_depth_map[
                        requirement.uid
                    ] = parent_depth
                    max_parent_depth = max(max_parent_depth, parent_depth)
            documents_ref_depth_map[document] = max(
                max_parent_depth, max_child_depth
            )
        traceability_index = TraceabilityIndex(
            document_iterators,
            requirements_map,
            tags_map,
            documents_ref_depth_map,
            document_parents_map,
            document_children_map,
            file_traceability_index,
        )
        return traceability_index
