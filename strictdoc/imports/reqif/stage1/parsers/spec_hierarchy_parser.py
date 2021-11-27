from strictdoc.imports.reqif.stage1.models.reqif_spec_hierarchy import (
    ReqIFSpecHierarchy,
)


class ReqIFSpecHierarchyParser:
    @staticmethod
    def parse(spec_hierarchy_xml, level=1) -> ReqIFSpecHierarchy:
        assert spec_hierarchy_xml.tag == "SPEC-HIERARCHY"
        attributes = spec_hierarchy_xml.attrib
        try:
            identifier = attributes["IDENTIFIER"]
        except Exception:
            raise NotImplementedError from None

        spec_hierarchy_children_xml = list(spec_hierarchy_xml)
        assert spec_hierarchy_children_xml[0].tag == "OBJECT"
        object_xml = spec_hierarchy_children_xml[0]
        spec_object_ref_xml = object_xml[0]
        assert spec_object_ref_xml.tag == "SPEC-OBJECT-REF"
        spec_object_ref = spec_object_ref_xml.text

        spec_hierarchy_children = []
        if len(spec_hierarchy_children_xml) == 2:
            assert spec_hierarchy_children_xml[1].tag == "CHILDREN"
            for child_spec_hierarchy_xml in spec_hierarchy_children_xml[1]:
                child_spec_hierarchy = ReqIFSpecHierarchyParser.parse(
                    child_spec_hierarchy_xml, level + 1
                )
                spec_hierarchy_children.append(child_spec_hierarchy)
        return ReqIFSpecHierarchy(
            identifier, spec_object_ref, spec_hierarchy_children, level
        )
