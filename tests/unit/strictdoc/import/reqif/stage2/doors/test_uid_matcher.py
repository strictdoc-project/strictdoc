from strictdoc.imports.reqif.stage2.doors.uid_matcher import match_letter_uid


def test_01():
    match = match_letter_uid("2.3.4")

    assert match is None


def test_02():
    match = match_letter_uid("2.3.4.a")

    assert match is "a"
