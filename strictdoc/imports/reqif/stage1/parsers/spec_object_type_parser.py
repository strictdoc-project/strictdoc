from strictdoc.imports.reqif.stage1.models.reqif_spec_object_type import (
    ReqIFSpecObjectType,
)


class SpecObjectTypeParser:
    @staticmethod
    def parse(spec_object_type_xml):
        assert spec_object_type_xml.tag == "SPEC-OBJECT-TYPE"
        attribute_map = {}

        attributes = spec_object_type_xml.attrib
        try:
            spec_type_id = attributes["IDENTIFIER"]
        except Exception:
            raise NotImplementedError

        try:
            spec_type_long_name = attributes["LONG-NAME"]
        except Exception:
            raise NotImplementedError

        spec_attributes = list(spec_object_type_xml)[0]
        for attribute_definition in spec_attributes:
            try:
                value = attribute_definition.attrib["LONG-NAME"]
                key = attribute_definition.attrib["IDENTIFIER"]
            except Exception:
                raise NotImplementedError(attribute_definition)
            attribute_map[key] = value

        return ReqIFSpecObjectType(
            spec_type_id, spec_type_long_name, attribute_map
        )
