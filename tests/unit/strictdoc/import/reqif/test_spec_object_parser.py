from xml.etree import ElementTree as etree

from strictdoc.imports.reqif.stage1.parsers.spec_object_parser import (
    SpecObjectParser,
)


def test_01_nominal_case():
    spec_object_string = """
<SPEC-OBJECT IDENTIFIER="TEST_SPEC_OBJECT_ID" LAST-CHANGE="2021-10-15T11:32:40.205+02:00">
  <VALUES>
    <ATTRIBUTE-VALUE-STRING THE-VALUE="SR001">
      <DEFINITION>
        <ATTRIBUTE-DEFINITION-STRING-REF>TEST_FIELD_UID</ATTRIBUTE-DEFINITION-STRING-REF>
      </DEFINITION>
    </ATTRIBUTE-VALUE-STRING>
    <ATTRIBUTE-VALUE-STRING THE-VALUE="Draft">
      <DEFINITION>
        <ATTRIBUTE-DEFINITION-STRING-REF>TEST_FIELD_STATUS</ATTRIBUTE-DEFINITION-STRING-REF>
      </DEFINITION>
    </ATTRIBUTE-VALUE-STRING>
    <ATTRIBUTE-VALUE-STRING THE-VALUE="Test statement">
      <DEFINITION>
        <ATTRIBUTE-DEFINITION-STRING-REF>TEST_FIELD_STATEMENT</ATTRIBUTE-DEFINITION-STRING-REF>
      </DEFINITION>
    </ATTRIBUTE-VALUE-STRING>
  </VALUES>
  <TYPE>
    <SPEC-OBJECT-TYPE-REF>TEST_SPEC_OBJECT_TYPE</SPEC-OBJECT-TYPE-REF>
  </TYPE>
</SPEC-OBJECT>
    """

    spec_object_xml = etree.fromstring(spec_object_string)
    spec_object = SpecObjectParser.parse(spec_object_xml)
    assert spec_object.identifier == "TEST_SPEC_OBJECT_ID"
    assert spec_object.spec_object_type == "TEST_SPEC_OBJECT_TYPE"
    assert spec_object.attribute_map == {
        "TEST_FIELD_UID": "SR001",
        "TEST_FIELD_STATUS": "Draft",
        "TEST_FIELD_STATEMENT": "Test statement",
    }
