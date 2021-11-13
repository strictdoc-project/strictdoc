from strictdoc.imports.reqif.stage1.models.reqif_specification import (
    ReqIFSpecification,
)
from strictdoc.imports.reqif.stage1.parsers.spec_hierarchy_parser import (
    ReqIFSpecHierarchyParser,
)


class ReqIFSpecificationParser:
    @staticmethod
    def parse(specification_xml):
        assert "SPECIFICATION" in specification_xml.tag, f"{specification_xml}"
        attributes = specification_xml.attrib
        try:
            identifier = attributes["IDENTIFIER"]
        except Exception:
            raise NotImplementedError

        specification_children_xml = list(specification_xml)
        # type_xml = None
        children_xml = None
        for specification_child_xml in specification_children_xml:
            if specification_child_xml.tag == "TYPE":
                pass  # type_xml = specification_child_xml
            elif specification_child_xml.tag == "CHILDREN":
                children_xml = specification_child_xml
        assert children_xml is not None

        children = []
        if children_xml is not None and len(children_xml):
            for child_xml in children_xml:
                spec_hierarchy_xml = ReqIFSpecHierarchyParser.parse(child_xml)
                children.append(spec_hierarchy_xml)
        return ReqIFSpecification(identifier, None, children)
