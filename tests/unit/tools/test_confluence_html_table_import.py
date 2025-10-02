import os

from bs4 import BeautifulSoup

from tools.confluence_html_table_import import ConfluenceHTMLTableImport

FIXTURES_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "fixtures")
)


def test_01():
    html_file = os.path.join(
        FIXTURES_PATH,
        (
            "001-confluence-html-file-two-sections/"
            "001-confluence-html-table-two-sections.html"
        ),
    )
    sdoc = ConfluenceHTMLTableImport.import_from_file(html_file)

    section1 = sdoc.section_contents[0]
    assert section1.reserved_title == "Section 1"
    section1_reqs = section1.section_contents
    assert section1_reqs[0].reserved_uid == "REQ-1-1 UID"
    assert section1_reqs[0].reserved_title == "REQ-1-1 Title"
    assert section1_reqs[0].reserved_statement == "REQ-1-1 Statement"
    assert section1_reqs[0].rationale == "REQ-1-1 Rationale"
    assert len(section1_reqs[0].get_comment_fields()) == 0

    assert section1_reqs[1].reserved_uid == "REQ-1-2 UID"
    assert section1_reqs[1].reserved_title == "REQ-1-2 Title"
    assert section1_reqs[1].reserved_statement == "REQ-1-2 Statement"
    assert section1_reqs[1].rationale == "REQ-1-2 Rationale"
    assert (
        section1_reqs[1].get_comment_fields()[0].get_text_value()
        == "REQ-1-2 Comment"
    )

    section2 = sdoc.section_contents[1]
    assert section2.reserved_title == "Section 2"
    section2_reqs = section2.section_contents
    assert section2_reqs[0].reserved_uid == "REQ-2-1 UID"
    assert section2_reqs[0].reserved_title == "REQ-2-1 Title"
    assert section2_reqs[0].reserved_statement == "REQ-2-1 Statement"
    assert section2_reqs[0].rationale == "REQ-2-1 Rationale"
    assert len(section2_reqs[0].get_comment_fields()) == 0

    assert section2_reqs[1].reserved_uid == "REQ-2-2 UID"
    assert section2_reqs[1].reserved_title == "REQ-2-2 Title"
    assert section2_reqs[1].reserved_statement == "REQ-2-2 Statement"
    assert section2_reqs[1].rationale == "REQ-2-2 Rationale"
    assert (
        section2_reqs[1].get_comment_fields()[0].get_text_value()
        == "REQ-2-2 Comment"
    )


def test_02():
    html_file = os.path.join(
        FIXTURES_PATH,
        (
            "002-confluence-html-file-parsing-paragraphs/"
            "002-confluence-html-table-parsing-paragraphs.html"
        ),
    )
    sdoc = ConfluenceHTMLTableImport.import_from_file(html_file)

    assert len(sdoc.section_contents) == 1

    section1 = sdoc.section_contents[0]
    assert section1.reserved_title == "Section 1"
    section1_reqs = section1.section_contents
    assert section1_reqs[0].reserved_uid == "REQ-1-1 UID"
    assert section1_reqs[0].reserved_title == "REQ-1-1 Title"
    assert section1_reqs[0].reserved_statement == "REQ-1-1 Statement"
    assert section1_reqs[0].rationale == "REQ-1-1 Rationale"
    assert len(section1_reqs[0].get_comment_fields()) == 1
    assert (
        section1_reqs[0].get_comment_fields()[0].get_text_value()
        == "REQ-1-1 comment wrapped in p"
    )
    assert (
        section1_reqs[1].get_comment_fields()[0].get_text_value()
        == "- Item 1\n- Item 2"
    )


def test_fragments_01():
    html_content = "<html><td>REQ-1-1 Statement</td></html>"
    soup = BeautifulSoup(html_content, "xml")
    td = soup.find("td")
    assert td

    text = ConfluenceHTMLTableImport.parse_tag_to_text(td)

    assert text == "REQ-1-1 Statement"


def test_fragments_02():
    html_content = "<html><td><p>REQ-1-1</p><p>Statement</p></td></html>"
    soup = BeautifulSoup(html_content, "xml")
    td = soup.find("td")
    assert td

    text = ConfluenceHTMLTableImport.parse_tag_to_text(td)

    assert text == "REQ-1-1\n\nStatement"


def test_fragments_03():
    html_content = (
        "<html><td><ul><li>Item 1</li><li>Item 2</li></ul></td></html>"
    )
    soup = BeautifulSoup(html_content, "xml")
    td = soup.find("td")
    assert td

    text = ConfluenceHTMLTableImport.parse_tag_to_text(td)

    assert text == "- Item 1\n- Item 2"
