from strictdoc.backend.dsl.models.requirement import Requirement
from strictdoc.core.document_iterator import DocumentCachingIterator
from strictdoc.core.document_tree import DocumentTree
from strictdoc.helpers.sorting import alphanumeric_sort


class TraceabilityIndex:
    @staticmethod
    def create(document_tree: DocumentTree):
        requirements_map = {}
        requirements_children_map = {}
        tags_map = {}
        document_iterators = {}

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
        # - Calculate depth of both parent and child links.
        for document in document_tree.document_list:
            document_iterator = DocumentCachingIterator(document)
            document_iterators[document] = document_iterator

            if document.name not in tags_map:
                tags_map[document.name] = {}

            for section_or_requirement in document_iterator.all_content():
                if not section_or_requirement.is_requirement:
                    continue

                requirement: Requirement = section_or_requirement
                if not requirement.uid:
                    continue

                document_tags = tags_map[document.name]
                for tag in requirement.tags:
                    if tag not in document_tags:
                        document_tags[tag] = 0
                    document_tags[tag] += 1

                if requirement.uid in requirements_map:
                    print('error: DocumentIndex: requirement already exists: {}'.format(
                        requirement.uid
                    ))
                    exit(1)

                if requirement.uid not in requirements_children_map:
                    requirements_children_map[requirement.uid] = []

                requirements_map[requirement.uid] = {
                    'document': document,
                    'requirement': requirement,
                    'parents': [],
                    'parents_uids': [],
                    'children': []
                }

                for ref in requirement.references:
                    if ref.ref_type != "Parent":
                        continue
                    requirements_map[requirement.uid]['parents_uids'].append(ref.path)

                    if ref.path not in requirements_children_map:
                        requirements_children_map[ref.path] = []
                    requirements_children_map[ref.path].append(requirement)

        # Now iterate over the requirements again to build an in-depth map of
        # parents and children.
        requirements_child_depth_map = {}
        requirements_parent_depth_map = {}
        documents_ref_depth_map = {}

        for document in document_tree.document_list:
            document_iterator = document_iterators[document]
            max_parent_depth, max_child_depth = 0, 0

            for section_or_requirement in document_iterator.all_content():
                if not section_or_requirement.is_requirement:
                    continue

                requirement: Requirement = section_or_requirement
                if not requirement.uid:
                    continue

                # Now it is possible to resolve parents first checking if they
                # indeed exist.
                requirement_parent_ids = requirements_map[requirement.uid]['parents_uids']
                for requirement_parent_id in requirement_parent_ids:
                    if requirement_parent_id not in requirements_map:
                        # TODO: Strict variant of the behavior will be to stop
                        # and raise an error message.
                        print("warning: [DocumentIndex.create] Requirement {} references parent requirement which doesn't exist: {}".format(
                            requirement.uid, requirement_parent_id
                        ))
                        requirements_children_map.pop(requirement_parent_id, None)
                        continue
                    parent_requirement = requirements_map[requirement_parent_id]['requirement']
                    requirements_map[requirement.uid]['parents'].append(parent_requirement)

                if requirement.uid not in requirements_child_depth_map:
                    child_depth = 0

                    requirements_map[requirement.uid]['children'] = requirements_children_map[requirement.uid]

                    queue = requirements_children_map[requirement.uid]
                    while True:
                        if len(queue) == 0:
                            break

                        child_depth += 1
                        deeper_queue = []
                        for child in queue:
                            deeper_queue.extend(requirements_children_map[child.uid])
                        queue = deeper_queue

                    requirements_child_depth_map[requirement.uid] = child_depth
                    if max_child_depth < child_depth:
                        max_child_depth = child_depth

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
                            deeper_queue.extend(requirements_map[parent_uid]['parents_uids'])
                        queue = deeper_queue

                    requirements_parent_depth_map[requirement.uid] = parent_depth
                    if max_parent_depth < parent_depth:
                        max_parent_depth = parent_depth

            documents_ref_depth_map[document] = max(max_parent_depth, max_child_depth)

        traceability_index = TraceabilityIndex(
            document_iterators,
            requirements_map,
            tags_map,
            documents_ref_depth_map
        )
        return traceability_index

    def __init__(self,
                 document_iterators,
                 requirements_parents,
                 tags_map,
                 documents_ref_depth_map):
        self._document_iterators = document_iterators
        self._requirements_parents = requirements_parents
        self._tags_map = tags_map
        self._documents_ref_depth_map = documents_ref_depth_map

    @property
    def document_iterators(self):
        return self._document_iterators

    @property
    def requirements_parents(self):
        return self._requirements_parents

    @property
    def tags_map(self):
        return self._tags_map

    @property
    def documents_ref_depth_map(self):
        return self._documents_ref_depth_map

    def get_document_iterator(self, document):
        return self.document_iterators[document]

    def get_parent_requirements(self, requirement: Requirement):
        assert isinstance(requirement, Requirement)
        if not isinstance(requirement.uid, str):
            return []

        if not requirement.uid or len(requirement.uid) == 0:
            return []

        if not self.requirements_parents:
            return []

        parent_requirements = self.requirements_parents[requirement.uid]['parents']
        return parent_requirements

    def has_parent_requirements(self, requirement: Requirement):
        assert isinstance(requirement, Requirement)
        if not isinstance(requirement.uid, str):
            return False

        if not requirement.uid or len(requirement.uid) == 0:
            return False

        if len(self.requirements_parents) == 0:
            return False

        parent_requirements = self.requirements_parents[requirement.uid]['parents']
        return len(parent_requirements) > 0

    def has_children_requirements(self, requirement: Requirement):
        assert isinstance(requirement, Requirement)
        if not isinstance(requirement.uid, str):
            return False

        if not requirement.uid or len(requirement.uid) == 0:
            return False

        if not self.requirements_parents:
            return False

        children_requirements = self.requirements_parents[requirement.uid]['children']
        return len(children_requirements) > 0

    def get_children_requirements(self, requirement: Requirement):
        assert isinstance(requirement, Requirement)
        if not isinstance(requirement.uid, str):
            return []

        if len(requirement.uid) == 0:
            return []

        if not self.requirements_parents:
            return []

        children_requirements = self.requirements_parents[requirement.uid]['children']
        return children_requirements

    def get_link(self, requirement):
        document = self.requirements_parents[requirement.uid]['document']
        return "{} - Traceability.html#{}".format(document.name, requirement.uid)

    def get_deep_link(self, requirement):
        document = self.requirements_parents[requirement.uid]['document']
        return "{} - Traceability Deep.html#{}".format(document.name, requirement.uid)

    def has_tags(self, document):
        if document.name not in self.tags_map:
            return False
        tags_bag = self.tags_map[document.name]
        return len(tags_bag.keys())

    def get_tags(self, document):
        assert document.name in self.tags_map
        tags_bag = self.tags_map[document.name]
        if not tags_bag:
            return []

        tags = sorted(tags_bag.keys(), key=alphanumeric_sort)
        for tag in tags:
            yield tag, tags_bag[tag]

    def get_max_ref_depth(self, document):
        return self.documents_ref_depth_map[document]
