# pragma: no cover file
import argparse
import os
import sys

import bs4
from bs4 import BeautifulSoup

from strictdoc.backend.sdoc.document_reference import DocumentReference
from strictdoc.backend.sdoc.models.document_grammar import DocumentGrammar
from strictdoc.backend.sdoc.models.object_factory import SDocObjectFactory

STRICTDOC_ROOT_PATH = os.path.join(os.path.dirname(__file__), "..")
sys.path.append(STRICTDOC_ROOT_PATH)

from strictdoc.backend.sdoc.models.document import SDocDocument
from strictdoc.backend.sdoc.models.section import SDocSection
from strictdoc.backend.sdoc.writer import SDWriter
from strictdoc.core.environment import SDocRuntimeEnvironment
from strictdoc.core.project_config import ProjectConfig


class ConfluenceHTMLTableImport:
    @staticmethod
    def import_from_file(path_to_html):
        if not os.path.isfile(path_to_html):
            sys.stdout.flush()
            err = f"Could not open doc file '{path_to_html}': No such file or directory."
            raise FileNotFoundError(err)

        with open(path_to_html) as file:
            html_content = file.read()

        soup = BeautifulSoup(html_content, "html5lib")

        headers = soup.find_all("h1", recursive=True)
        tables = soup.find_all("table", recursive=True)
        assert len(headers) == len(tables)

        reqs_array_array = []
        for reqs_table in soup.find_all("table", recursive=True):
            reqs = ConfluenceHTMLTableImport.parse_table(reqs_table)
            reqs_array_array.append(reqs)

        document = SDocDocument(
            mid=None,
            title="Imported Doc",
            config=None,
            grammar=None,
            view=None,
            section_contents=[],
        )
        document.grammar = DocumentGrammar.create_default(document)
        for section_idx, reqs in enumerate(reqs_array_array):
            section_name = headers[section_idx].text
            section = SDocSection(
                document, None,None, "1", section_name,
                requirement_prefix=None,
                section_contents=[]
            )
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
                    node_type="REQUIREMENT",
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
        for th_idx, th in enumerate(first_tr.find_all("th", recursive=False)):
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

        for tr in tbody.find_all("tr", recursive=False)[1:]:
            req_uid = tr.find_all("td", recursive=False)[field_to_index_map["UID"]].text
            req_type = tr.find_all("td", recursive=False)[field_to_index_map["TYPE"]].text
            req_title = tr.find_all("td", recursive=False)[field_to_index_map["TITLE"]].text
            req_statement = tr.find_all("td", recursive=False)[
                field_to_index_map["STATEMENT"]
            ].text
            req_comment = ConfluenceHTMLTableImport.parse_tag_to_text(
                tr.find_all("td", recursive=False)[field_to_index_map["COMMENT"]]
            )
            req_rationale = tr.find_all("td", recursive=False)[
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
        children = tag.find_all(recursive=False)
        if len(children) == 0:
            return tag.text
        paragraphs = []
        for child in children:
            if child.name == "ul":
                ul_rst_list = []
                for li in child.find_all(recursive=False):
                    assert li.name == "li"
                    ul_rst_list.append(f"- {li.text}")
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

    print(args.input_file)  # noqa: T201

    path_to_input_html = args.input_file
    if not os.path.isfile(path_to_input_html):
        print(f"not a file: {path_to_input_html}")  # noqa: T201
        exit(1)

    sdoc = ConfluenceHTMLTableImport.import_from_file(path_to_input_html)
    print(sdoc)  # noqa: T201

    project_config = ProjectConfig.default_config(SDocRuntimeEnvironment(__file__))
    sdoc_content = SDWriter(project_config).write(sdoc)
    with open("output.sdoc", "w") as output_file:
        output_file.write(sdoc_content)


if __name__ == "__main__":
    main()
