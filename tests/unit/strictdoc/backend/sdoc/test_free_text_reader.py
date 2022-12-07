from strictdoc.backend.sdoc.free_text_reader import SDFreeTextReader
from strictdoc.backend.sdoc.models.free_text import FreeText


def test_001_hello_world():
    free_text_input = """
Hello world [LINK: FOO] Part
""".lstrip()

    reader = SDFreeTextReader()

    document = reader.read(free_text_input)
    assert isinstance(document, FreeText)

    assert document.parts[0] == "Hello world "
    assert document.parts[1].link == "FOO"
    assert document.parts[2] == " Part\n"
