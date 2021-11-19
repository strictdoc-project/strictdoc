import collections
from typing import Dict, List, Deque

from strictdoc.imports.reqif.stage1.models.reqif_spec_hierarchy import (
    ReqIFSpecHierarchy,
)
from strictdoc.imports.reqif.stage1.models.reqif_spec_object import (
    ReqIFSpecObject,
)


class ReqIFBundle:
    @staticmethod
    def create_empty():
        return ReqIFBundle([], [], {}, [])

    def __init__(
        self,
        data_types,
        spec_objects: List,
        spec_objects_lookup: Dict,
        specifications,
    ):
        self.data_types = data_types
        self.spec_objects = spec_objects
        self.spec_objects_lookup = spec_objects_lookup

        self.specifications = specifications

    def get_spec_object_by_ref(self, ref) -> ReqIFSpecObject:
        return self.spec_objects_lookup[ref]

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
