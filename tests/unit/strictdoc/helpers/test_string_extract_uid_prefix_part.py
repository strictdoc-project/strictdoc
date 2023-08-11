from strictdoc.helpers.string import extract_numeric_uid_prefix_part


def test():
    assert extract_numeric_uid_prefix_part("REQ-0") == "REQ-"
    assert extract_numeric_uid_prefix_part("REQ-001") == "REQ-"
    assert extract_numeric_uid_prefix_part("REQ.001") == "REQ."
    assert extract_numeric_uid_prefix_part("REQ_001") == "REQ_"

    assert extract_numeric_uid_prefix_part("AGW-S-001") == "AGW-S-"
    assert extract_numeric_uid_prefix_part("LEVEL1-REQ-1") == "LEVEL1-REQ-"

    assert extract_numeric_uid_prefix_part("0") is None
    assert extract_numeric_uid_prefix_part("") is None
    assert extract_numeric_uid_prefix_part("REQ") is None
    assert extract_numeric_uid_prefix_part("REQ-") is None
