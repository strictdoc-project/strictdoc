from strictdoc.helpers.text_width import (
    LAST_CODE_POINT,
    double_width_ranges,
    is_double_width,
    text_width,
)


def test_01_text_width():
    assert text_width("abc") == 3
    assert text_width("中文") == 4
    assert text_width("😀") == 2
    assert text_width("é") == 1
    assert text_width("𝔸") == 1


def test_02_double_width_ranges_match_is_double_width():
    ranges = double_width_ranges()

    previous_last = -2
    for first_, last_ in ranges:
        # The ranges are in ascending order, and two ranges never touch.
        assert previous_last + 1 < first_ <= last_
        previous_last = last_

    in_ranges = [False] * (LAST_CODE_POINT + 1)
    for first_, last_ in ranges:
        for code_point_ in range(first_, last_ + 1):
            in_ranges[code_point_] = True
    for code_point_ in range(LAST_CODE_POINT + 1):
        assert in_ranges[code_point_] == is_double_width(chr(code_point_))
