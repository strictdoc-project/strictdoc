from strictdoc.imports.reqif.stage1.models.reqif_spec_relation import (
    ReqIFSpecRelation,
)


class SpecRelationParser:
    @staticmethod
    def parse(xml_spec_relation) -> ReqIFSpecRelation:
        assert xml_spec_relation.tag == "SPEC-RELATION"
        attributes = xml_spec_relation.attrib

        assert "IDENTIFIER" in attributes, f"{attributes}"
        identifier = attributes["IDENTIFIER"]

        relation_type_ref = (
            xml_spec_relation.find("TYPE").find("SPEC-RELATION-TYPE-REF").text
        )
        spec_relation_source = (
            xml_spec_relation.find("SOURCE").find("SPEC-OBJECT-REF").text
        )
        spec_relation_target = (
            xml_spec_relation.find("TARGET").find("SPEC-OBJECT-REF").text
        )

        spec_relation = ReqIFSpecRelation(
            identifier=identifier,
            relation_type_ref=relation_type_ref,
            source=spec_relation_source,
            target=spec_relation_target,
        )
        return spec_relation
