from strictdoc.helpers.string import multireplace


def test_multireplace_01():
    input_string = "hey abc"
    replacements = {"ab": "AB", "abc": "ABC"}
    result = multireplace(input_string, replacements)
    assert result == "hey ABC"

    input_string = "REQ1, REQ12"
    replacements = {"REQ1": "!REQ1", "REQ12": "!REQ12"}
    result = multireplace(input_string, replacements)
    assert result == "!REQ1, !REQ12"

    input_string = "REQ12, REQ1"
    replacements = {"REQ1": "!REQ1", "REQ12": "!REQ12"}
    result = multireplace(input_string, replacements)
    assert result == "!REQ12, !REQ1"
