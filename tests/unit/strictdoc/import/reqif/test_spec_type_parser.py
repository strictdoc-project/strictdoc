from xml.etree import ElementTree as etree

from strictdoc.imports.reqif.stage1.models.reqif_spec_object_type import (
    ReqIFSpecObjectType,
)
from strictdoc.imports.reqif.stage1.parsers.spec_object_type_parser import (
    SpecObjectTypeParser,
)


def test_01_nominal_case():
    spec_type_string = """
<SPEC-OBJECT-TYPE IDENTIFIER="_gFhrWmojEeuExICsU7Acmg" LAST-CHANGE="2021-02-08T16:37:07.454+01:00" LONG-NAME="FUNCTIONAL">
  <SPEC-ATTRIBUTES>
    <ATTRIBUTE-DEFINITION-STRING IDENTIFIER="_gFhrW2ojEeuExICsU7Acmg" LAST-CHANGE="2021-02-08T16:37:07.454+01:00" LONG-NAME="ReqIF.ForeignID">
      <TYPE>
        <DATATYPE-DEFINITION-STRING-REF>_gFhrVGojEeuExICsU7Acmg</DATATYPE-DEFINITION-STRING-REF>
      </TYPE>
    </ATTRIBUTE-DEFINITION-STRING>
    <ATTRIBUTE-DEFINITION-STRING DESC="Testattribute" IDENTIFIER="_aqZG4GxpEeuaU7fHySy8Bw" LAST-CHANGE="2021-02-11T14:02:05.129+01:00" LONG-NAME="NOTES" IS-EDITABLE="true">
      <TYPE>
        <DATATYPE-DEFINITION-STRING-REF>_gFhrU2ojEeuExICsU7Acmg</DATATYPE-DEFINITION-STRING-REF>
      </TYPE>
      <DEFAULT-VALUE/>
    </ATTRIBUTE-DEFINITION-STRING>
  </SPEC-ATTRIBUTES>
</SPEC-OBJECT-TYPE>
    """
    spec_type_xml = etree.fromstring(spec_type_string)

    reqif_spec_object_type = SpecObjectTypeParser.parse(spec_type_xml)
    assert isinstance(reqif_spec_object_type, ReqIFSpecObjectType)
    assert reqif_spec_object_type.identifier == "_gFhrWmojEeuExICsU7Acmg"
    assert reqif_spec_object_type.long_name == "FUNCTIONAL"
    attribute_map = reqif_spec_object_type.attribute_map
    assert len(attribute_map) == 2
    assert attribute_map.get("_gFhrW2ojEeuExICsU7Acmg") == "ReqIF.ForeignID"
    assert attribute_map.get("_aqZG4GxpEeuaU7fHySy8Bw") == "NOTES"
