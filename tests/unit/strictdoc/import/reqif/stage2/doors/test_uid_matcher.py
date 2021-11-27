from strictdoc.imports.reqif.stage2.doors.uid_matcher import (
    match_letter_uid,
    match_bullet_uid,
    match_continuation_uid,
)


def test_match_letter_uid():
    assert match_letter_uid("2.3.4") is None
    assert match_letter_uid("2.3.4.a") == "a"


def test_match_bullet_uid():
    assert match_bullet_uid("2.3.4") is None
    assert match_bullet_uid("3.4.4.1.1.*[2]") == "2"


def test_match_continuation_uid():
    assert match_continuation_uid("2.3.4") is None
    assert match_continuation_uid("3.5.3.7.a[2]") == "2"
