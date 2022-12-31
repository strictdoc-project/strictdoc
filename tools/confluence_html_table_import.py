import argparse
import os
import sys

import bs4
from bs4 import BeautifulSoup

from strictdoc.backend.sdoc.document_reference import DocumentReference
from strictdoc.backend.sdoc.models.object_factory import SDocObjectFactory

STRICTDOC_ROOT_PATH = os.path.join(os.path.dirname(__file__), "..")
sys.path.append(STRICTDOC_ROOT_PATH)

from strictdoc.backend.sdoc.writer import SDWriter
from strictdoc.backend.sdoc.models.document import Document
from strictdoc.backend.sdoc.models.requirement import (
    Requirement,
    RequirementComment,
)
from strictdoc.backend.sdoc.models.section import Section


class ConfluenceHTMLTableImport:
    @staticmethod
    def import_from_file(path_to_html):
        if not os.path.isfile(path_to_html):
            sys.stdout.flush()
            err = f"Could not open doc file '{path_to_html}': No such file or directory."
            raise FileNotFoundError(err)

        with open(path_to_html, "r") as file:
            html_content = file.read()

        soup = BeautifulSoup(html_content, "html5lib")

        headers = soup.findChildren("h1")
        tables = soup.findChildren("table")
        assert len(headers) == len(tables)

        reqs_array_array = []
        for reqs_table in soup.findChildren("table"):
            reqs = ConfluenceHTMLTableImport.parse_table(reqs_table)
            reqs_array_array.append(reqs)

        document = Document(
            title="Imported Doc",
            config=None,
            grammar=None,
            free_texts=[],
            section_contents=[],
        )
        for section_idx, reqs in enumerate(reqs_array_array):
            section_name = headers[section_idx].text
            section = Section(document, None, "1", section_name, [], [])
            section.ng_document_reference = DocumentReference()
            section.ng_document_reference.set_document(document)
            document.section_contents.append(section)
            for req in reqs:
                uid = req["UID"]
                title = req["TITLE"]
                statement = req["STATEMENT"]
                rationale = req["RATIONALE"]
                comment = req["COMMENT"]
                sreq = SDocObjectFactory.create_requirement(
                    parent=section,
                    requirement_type="REQUIREMENT",
                    uid=uid,
                    level=None,
                    title=title,
                    statement=None,
                    statement_multiline=statement,
                    rationale=None,
                    rationale_multiline=rationale,
                    tags=None,
                    comments=[comment] if len(comment) else None,
                )
                sreq.ng_level = 2
                section.section_contents.append(sreq)

        return document

    @staticmethod
    def parse_table(reqs_table):
        tbody: bs4.element.Tag = reqs_table.find("tbody")

        first_tr: bs4.element.Tag = tbody.find("tr")

        field_to_index_map = {
            "UID": -1,
            "TYPE": -1,
            "TITLE": -1,
            "STATEMENT": -1,
            "COMMENT": -1,
            "RATIONALE": -1,
        }
        for th_idx, th in enumerate(first_tr.findChildren("th")):
            content_wrapper_div = th.find("div", class_="content-wrapper")
            if content_wrapper_div:
                p = content_wrapper_div.find("p")
                if p:
                    text = p.contents[0]
                else:
                    text = content_wrapper_div.text
                assert isinstance(text, str)
            else:
                text = th.text

            if text == "ID":
                field_to_index_map["UID"] = th_idx
            elif text == "Title":
                field_to_index_map["TITLE"] = th_idx
            elif text == "Requirement":
                field_to_index_map["STATEMENT"] = th_idx
            elif text == "Remark":
                field_to_index_map["COMMENT"] = th_idx
            elif text == "Rationale":
                field_to_index_map["RATIONALE"] = th_idx
            elif text == "Requirement Type":
                field_to_index_map["TYPE"] = th_idx

        reqs = []

        for tr in tbody.findChildren("tr")[1:]:
            req_uid = tr.findChildren("td")[field_to_index_map["UID"]].text
            req_type = tr.findChildren("td")[field_to_index_map["TYPE"]].text
            req_title = tr.findChildren("td")[field_to_index_map["TITLE"]].text
            req_statement = tr.findChildren("td")[
                field_to_index_map["STATEMENT"]
            ].text
            req_comment = ConfluenceHTMLTableImport.parse_tag_to_text(
                tr.findChildren("td")[field_to_index_map["COMMENT"]]
            )
            req_rationale = tr.findChildren("td")[
                field_to_index_map["RATIONALE"]
            ].text

            reqs.append(
                {
                    "UID": req_uid.strip(),
                    "TYPE": req_type.strip(),
                    "TITLE": req_title.strip(),
                    "STATEMENT": req_statement.strip(),
                    "COMMENT": req_comment.strip(),
                    "RATIONALE": req_rationale.strip(),
                }
            )

        return reqs

    @staticmethod
    def parse_tag_to_text(tag):
        # The parsing below is too primitive but it works for now.
        # TODO: Consider implementing an HTML->RST converter.
        children = tag.findChildren(recursive=False)
        if len(children) == 0:
            return tag.text
        paragraphs = []
        for child in children:
            if child.name == "ul":
                ul_rst_list = []
                for li in child.findChildren(recursive=False):
                    assert li.name == "li"
                    ul_rst_list.append("- {}".format(li.text))
                paragraphs.append("\n".join(ul_rst_list))
                continue
            child_text = ConfluenceHTMLTableImport.parse_tag_to_text(child)
            paragraphs.append(child_text)
        return "\n\n".join(paragraphs)


def main():
    ROOT_PATH = os.path.join(os.path.dirname(__file__), "..")
    sys.path.append(ROOT_PATH)

    parser = argparse.ArgumentParser()

    parser.add_argument("input_file", type=str, help="TODO")
    parser.add_argument("--output-file", type=str, help="TODO")
    args = parser.parse_args()

    print(args.input_file)

    path_to_input_html = args.input_file
    if not os.path.isfile(path_to_input_html):
        print("not a file: {}".format(path_to_input_html))
        exit(1)

    sdoc = ConfluenceHTMLTableImport.import_from_file(path_to_input_html)
    print(sdoc)

    sdoc_content = SDWriter().write(sdoc)
    with open("output.sdoc", "w") as output_file:
        output_file.write(sdoc_content)


if __name__ == "__main__":
    main()
