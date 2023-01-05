from strictdoc.helpers.string import multireplace, sanitize_html_form_field


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


def test_sanitize_01_trims_all_fields_in_initializer_spaces():
    field = """
        Hello world!        
    """  # noqa: W291
    sanitized_field = sanitize_html_form_field(field, multiline=False)
    assert sanitized_field == "Hello world!"

    sanitized_field = sanitize_html_form_field(field, multiline=True)
    assert sanitized_field == "Hello world!"


def test_sanitize_02_trims_all_fields_in_initializer_newlines():
    field = """
        \n\n    Hello world!   \n\n     
    """  # noqa: W291
    sanitized_field = sanitize_html_form_field(field, multiline=False)
    assert sanitized_field == "Hello world!"

    sanitized_field = sanitize_html_form_field(field, multiline=True)
    assert sanitized_field == "Hello world!"


def test_sanitize_10_removes_all_trailing_whitespace_in_initializer():
    # section statement below contains newlines:
    field = """
Hello world!    

Hello world!    

Hello world!    
    """  # noqa: W291
    sanitized_field = sanitize_html_form_field(field, multiline=True)
    assert sanitized_field == "Hello world!\n\nHello world!\n\nHello world!"


def test_sanitize_04_single_line_removes_all_newlines():
    field = """
        Hello world!        
        Hello world!
        Hello world!
    """  # noqa: W291
    sanitized_field = sanitize_html_form_field(field, multiline=False)
    assert sanitized_field == "Hello world! Hello world! Hello world!"
