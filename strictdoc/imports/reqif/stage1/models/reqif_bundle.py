import collections
from typing import Dict, List, Deque

from strictdoc.imports.reqif.stage1.models.reqif_spec_hierarchy import (
    ReqIFSpecHierarchy,
)
from strictdoc.imports.reqif.stage1.models.reqif_spec_object import (
    ReqIFSpecObject,
)
from strictdoc.imports.reqif.stage1.models.reqif_spec_object_type import (
    ReqIFSpecObjectType,
)
from strictdoc.imports.reqif.stage1.models.reqif_spec_relation import (
    ReqIFSpecRelation,
)
from strictdoc.imports.reqif.stage1.models.reqif_specification import (
    ReqIFSpecification,
)


class ReqIFBundle:
    @staticmethod
    def create_empty():
        return ReqIFBundle(
            data_types=[],
            spec_object_types=[],
            spec_objects=[],
            spec_objects_lookup={},
            spec_relations=[],
            spec_relations_parent_lookup={},
            specifications=[],
        )

    def __init__(
        self,
        data_types,
        spec_object_types: List[ReqIFSpecObjectType],
        spec_objects: List[ReqIFSpecObject],
        spec_objects_lookup: Dict,
        spec_relations: List[ReqIFSpecRelation],
        spec_relations_parent_lookup: Dict[str, List[ReqIFSpecRelation]],
        specifications: List[ReqIFSpecification],
    ):
        self.data_types = data_types
        self.spec_object_types = spec_object_types
        self.spec_objects = spec_objects
        self.spec_objects_lookup = spec_objects_lookup
        self.spec_relations = spec_relations
        self.spec_relations_parent_lookup = spec_relations_parent_lookup
        self.specifications = specifications

    def get_spec_object_by_ref(self, ref) -> ReqIFSpecObject:
        return self.spec_objects_lookup[ref]

    def get_spec_object_parents(self, ref) -> List:
        return self.spec_relations_parent_lookup[ref]

    def iterate_specification_hierarchy(self, specification):
        assert specification in self.specifications

        task_list: Deque[ReqIFSpecHierarchy] = collections.deque(
            specification.children
        )

        while True:
            if not task_list:
                break
            current = task_list.popleft()

            yield current

            task_list.extendleft(reversed(current.children))
