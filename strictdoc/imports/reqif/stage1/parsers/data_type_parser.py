from lxml import etree

from strictdoc.imports.reqif.stage1.models.reqif_data_type import (
    ReqIFDataTypeDefinitionString,
    ReqIFDataTypeDefinitionEnumeration,
)


class DataTypeParser:
    @staticmethod
    def parse(data_type_xml):
        assert "DATATYPE-DEFINITION-" in data_type_xml.tag
        attributes = data_type_xml.attrib
        identifier = attributes["IDENTIFIER"]

        values_map = {}

        if data_type_xml.tag == "DATATYPE-DEFINITION-ENUMERATION":
            specified_values = data_type_xml.find("SPECIFIED-VALUES")

            for specified_value in specified_values:
                specified_value_attributes = specified_value.attrib
                specified_value_identifier = specified_value_attributes[
                    "IDENTIFIER"
                ]

                properties = specified_value.find("PROPERTIES")

                embedded_value = properties.find("EMBEDDED-VALUE")
                embedded_value_attributes = embedded_value.attrib
                embedded_value_key = embedded_value_attributes["KEY"]

                values_map[specified_value_identifier] = embedded_value_key
            return ReqIFDataTypeDefinitionEnumeration(identifier, values_map)
        elif data_type_xml.tag == "DATATYPE-DEFINITION-STRING":
            return ReqIFDataTypeDefinitionString(identifier)

        # TODO: All the following is parsed to just String.
        elif data_type_xml.tag == "DATATYPE-DEFINITION-INTEGER":
            return ReqIFDataTypeDefinitionString(identifier)
        elif data_type_xml.tag == "DATATYPE-DEFINITION-XHTML":
            return ReqIFDataTypeDefinitionString(identifier)
        elif data_type_xml.tag == "DATATYPE-DEFINITION-BOOLEAN":
            return ReqIFDataTypeDefinitionString(identifier)
        raise NotImplementedError(etree.tostring(data_type_xml))
