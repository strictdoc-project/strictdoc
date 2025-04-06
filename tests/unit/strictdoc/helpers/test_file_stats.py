from strictdoc.helpers.file_stats import SourceFileStats


def test_create():
    input_string = "Line 1\n\nLine 3\n  \nLine 5"
    stats = SourceFileStats.create(input_string)

    assert stats.lines_total == 5
    assert stats.lines_non_empty == 3
    assert stats.lines_empty == 2

    assert stats.lines_info[1] == True
    assert stats.lines_info[2] == False
    assert stats.lines_info[3] == True
    assert stats.lines_info[4] == False
    assert stats.lines_info[5] == True
