from strictdoc.backend.dsl.models import Requirement
from strictdoc.core.document_tree import DocumentTree


class TraceabilityIndex:
    @staticmethod
    def create(document_tree: DocumentTree):
        requirements_map = {}

        for document in document_tree.document_list:
            for section_or_requirement in document.ng_section_iterator():
                if not section_or_requirement.is_requirement:
                    continue

                requirement: Requirement = section_or_requirement
                if not requirement.uid:
                    continue

                if requirement.uid not in requirements_map:
                    requirements_map[requirement.uid] = {
                        'document': document,
                        'requirement': requirement,
                        'parents': [],
                        'children': []
                    }
                requirements_map[requirement.uid]['requirement'] = requirement
                requirements_map[requirement.uid]['document'] = document

                for ref in requirement.references:
                    if ref.ref_type != "Parent":
                        continue

                    requirements_map[requirement.uid]['parents'].append(ref)
                    if ref.path not in requirements_map:
                        requirements_map[ref.path] = {
                            'parents': [],
                            'children': []
                        }
                    requirements_map[ref.path]['children'].append(requirement)

        # Now iterate over the requirements again to build an in-depth map of
        # parents and children.
        max_parent_depth, max_child_depth = 0, 0

        requirements_child_depth_map = {}
        for document in document_tree.document_list:
            for section_or_requirement in document.ng_section_iterator():
                if not section_or_requirement.is_requirement:
                    continue

                requirement: Requirement = section_or_requirement
                if not requirement.uid:
                    continue

                if requirement.uid in requirements_child_depth_map:
                    continue

                parent_depth, child_depth = 0, 0

                queue = requirements_map[requirement.uid]['children']
                while True:
                    if len(queue) == 0:
                        break

                    child_depth += 1
                    deeper_queue = []
                    for child in queue:
                        deeper_queue.extend(requirements_map[child.uid]['children'])
                    queue = deeper_queue
                requirements_child_depth_map[requirement.uid] = child_depth
                if max_child_depth < child_depth:
                    max_child_depth = child_depth

        print("child depth: {}".format(max_child_depth))
        print("child depth: {}".format(requirements_child_depth_map))

        traceability_index = TraceabilityIndex(requirements_map, max_child_depth)
        return traceability_index

    def __init__(self, requirements_parents, max_child_depth):
        self.requirements_parents = requirements_parents
        self.max_child_depth = max_child_depth

    def get_parent_requirements(self, requirement: Requirement):
        assert isinstance(requirement, Requirement)
        assert isinstance(requirement.uid, str)

        if not requirement.uid or len(requirement.uid) == 0:
            return []

        if not self.requirements_parents:
            return []

        parent_requirements = []
        parent_references = self.requirements_parents[requirement.uid]['parents']
        for ref in parent_references:
            if ref.path not in self.requirements_parents:
                continue
            if 'requirement' not in self.requirements_parents[ref.path]:
                print(ref.path)
                continue
            parent_requirements.append(self.requirements_parents[ref.path]['requirement'])
        return parent_requirements

    def get_children_requirements(self, requirement: Requirement):
        assert isinstance(requirement, Requirement)
        assert isinstance(requirement.uid, str)

        if not requirement.uid or len(requirement.uid) == 0:
            return []

        if not self.requirements_parents:
            return []

        children_requirements = self.requirements_parents[requirement.uid]['children']
        return children_requirements

    def get_link(self, requirement):
        document = self.requirements_parents[requirement.uid]['document']
        return "{} - Traceability.html#{}".format(document.name, requirement.uid)