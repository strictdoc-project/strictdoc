from strictdoc.backend.rst.rst_field_parser import RSTFieldParser


def test_01_one_record_per_line():
    input = """
- key1_1 = value1_1, key1_2 = value1_2
- key2_1 = value2_1, key2_2 = value2_2
"""

    output = RSTFieldParser.parse_dict_array(input)

    assert output[0]['key1_1'] == 'value1_1'
    assert output[0]['key1_2'] == 'value1_2'
    assert output[1]['key2_1'] == 'value2_1'
    assert output[1]['key2_2'] == 'value2_2'


def test_02_record_per_multiple_lines():
    input = """
- key1_1 = value1_1, 
  key1_2 = value1_2
- key2_1 = value2_1, 
  key2_2 = value2_2
"""

    output = RSTFieldParser.parse_dict_array(input)

    assert output[0]['key1_1'] == 'value1_1'
    assert output[0]['key1_2'] == 'value1_2'
    assert output[1]['key2_1'] == 'value2_1'
    assert output[1]['key2_2'] == 'value2_2'
