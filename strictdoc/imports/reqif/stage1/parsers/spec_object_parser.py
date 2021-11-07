from lxml import etree

from strictdoc.imports.reqif.stage1.models.reqif_spec_object import (
    ReqIFSpecObject,
)


class SpecObjectParser:
    @staticmethod
    def parse(spec_object_xml) -> ReqIFSpecObject:
        assert "SPEC-OBJECT" in spec_object_xml.tag
        attributes = spec_object_xml.attrib

        try:
            identifier = attributes["IDENTIFIER"]
        except Exception:
            raise NotImplementedError

        spec_object_type = (
            spec_object_xml.find("TYPE").find("SPEC-OBJECT-TYPE-REF").text
        )

        attribute_map = {}
        for attribute_xml in spec_object_xml[0]:
            if attribute_xml.tag == "ATTRIBUTE-VALUE-STRING":
                attribute_value = attribute_xml.attrib["THE-VALUE"]
                attribute_name = attribute_xml[0][0].text
            elif attribute_xml.tag == "ATTRIBUTE-VALUE-ENUMERATION":
                attribute_value = (
                    attribute_xml.find("VALUES").find("ENUM-VALUE-REF").text
                )
                attribute_name = (
                    attribute_xml.find("DEFINITION")
                    .find("ATTRIBUTE-DEFINITION-ENUMERATION-REF")
                    .text
                )
            elif attribute_xml.tag == "ATTRIBUTE-VALUE-INTEGER":
                attribute_value = attribute_xml.attrib["THE-VALUE"]

                attribute_name = (
                    attribute_xml.find("DEFINITION")
                    .find("ATTRIBUTE-DEFINITION-INTEGER-REF")
                    .text
                )
            elif attribute_xml.tag == "ATTRIBUTE-VALUE-BOOLEAN":
                attribute_value = attribute_xml.attrib["THE-VALUE"]

                attribute_name = (
                    attribute_xml.find("DEFINITION")
                    .find("ATTRIBUTE-DEFINITION-BOOLEAN-REF")
                    .text
                )
            elif attribute_xml.tag == "ATTRIBUTE-VALUE-XHTML":
                attribute_value = attribute_xml.find("THE-VALUE").text

                attribute_name = (
                    attribute_xml.find("DEFINITION")
                    .find("ATTRIBUTE-DEFINITION-XHTML-REF")
                    .text
                )
            else:
                raise NotImplementedError(etree.tostring(attribute_xml))
            attribute_map[attribute_name] = attribute_value

        return ReqIFSpecObject(identifier, spec_object_type, attribute_map)
