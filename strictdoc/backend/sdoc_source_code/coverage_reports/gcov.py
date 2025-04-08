import hashlib
import json
import os
from enum import IntEnum
from pathlib import Path
from typing import Any, List, Optional, Union

import bs4
from bs4 import BeautifulSoup

from strictdoc.backend.sdoc.document_reference import DocumentReference
from strictdoc.backend.sdoc.models.document import SDocDocument
from strictdoc.backend.sdoc.models.document_grammar import DocumentGrammar
from strictdoc.backend.sdoc.models.node import SDocNode, SDocNodeField
from strictdoc.backend.sdoc.models.reference import FileReference
from strictdoc.backend.sdoc.models.section import SDocSection
from strictdoc.backend.sdoc.models.type_system import FileEntry, FileEntryFormat
from strictdoc.core.file_tree import File
from strictdoc.core.project_config import ProjectConfig
from strictdoc.helpers.cast import assert_cast, assert_optional_cast
from strictdoc.helpers.paths import path_to_posix_path


class GCovJSONReader:
    @classmethod
    def read_from_file(
        cls: "GCovJSONReader", doc_file: File, project_config: ProjectConfig
    ) -> SDocDocument:
        with open(doc_file.get_full_path(), encoding="UTF-8") as file:
            content = file.read()
        return cls.read_from_string(content, doc_file, project_config)

    @classmethod
    def read_from_string(
        cls: "GCovJSONReader",
        content: str,
        doc_file: File,
        project_config: ProjectConfig,
    ) -> SDocDocument:
        if len(content) == 0:
            raise RuntimeError(
                "Document is empty"
            )
        try:
            json_content = json.loads(content)
        except Exception as exception:  # pylint: disable=broad-except
            raise RuntimeError(str(exception)) from None

        document = SDocDocument(
            mid=None,
            title="Test report",
            config=None,
            view=None,
            grammar=None,
            section_contents=[],
        )
        document.ng_including_document_reference = DocumentReference()
        grammar = DocumentGrammar.create_for_test_report(document)
        document.grammar = grammar
        document.config.requirement_style = "Table"

        summary_table = f"""\
.. list-table:: Test suite summary
    :widths: 25 10
    :header-rows: 0
    
    * - **Number of tests:**
      - FOO
    * - **Number of successful tests:**
      - BAR
"""

        testcase_node = SDocNode(
            parent=document,
            node_type="TEXT",
            fields=[],
            relations=[],
        )
        testcase_node.ng_document_reference = DocumentReference()
        testcase_node.ng_document_reference.set_document(document)
        testcase_node.ng_including_document_reference = DocumentReference()
        testcase_node.set_field_value(
            field_name="STATEMENT",
            form_field_index=0,
            value=SDocNodeField(
                parent=testcase_node,
                field_name="STATEMENT",
                parts=[summary_table],
                multiline__="True",
            ),
        )
        document.section_contents.append(testcase_node)

        """
        Parse individual <testcase> elements.
        """

        json_files = json_content["files"]
        for json_file_ in json_files:
            json_file_name = json_file_["file"]

            file_section = SDocSection(
                parent=document,
                mid=None,
                uid=None,
                custom_level=None,
                title=json_file_name,
                requirement_prefix=None,
                section_contents=[],
            )
            file_section.ng_including_document_reference = (
                DocumentReference()
            )
            file_section.ng_document_reference = DocumentReference()
            file_section.ng_document_reference.set_document(document)
            document.section_contents.append(file_section)

            for json_function_ in json_file_["functions"]:
                json_function_name = json_function_["demangled_name"]

                testcase_node = SDocNode(
                    parent=document,
                    node_type="TEST_RESULT",
                    fields=[],
                    relations=[],
                )
                testcase_node.ng_document_reference = DocumentReference()
                testcase_node.ng_document_reference.set_document(document)
                testcase_node.ng_including_document_reference = (
                    DocumentReference()
                )
                testcase_node.set_field_value(
                    field_name="UID",
                    form_field_index=0,
                    value=SDocNodeField(
                        parent=testcase_node,
                        field_name="UID",
                        parts=["GCOV:" + json_file_name + ":" + json_function_name],
                        multiline__=None,
                    ),
                )

                path = "src/main.c"
                hash = hashlib.md5(path.encode("utf-8")).hexdigest()
                link = "../../../../" + "coverage." + Path(json_file_name).name + ". " + hash + ".html"
                testcase_node.set_field_value(
                    field_name="STATEMENT",
                    form_field_index=0,
                    value=SDocNodeField(
                        parent=testcase_node,
                        field_name="STATEMENT",
                        parts=[
                            f"""
                            `LINK <{link}>`_
                            """

                        ],
                        multiline__=None,
                    ),
                )
                # if test_case_node_test_function is not None:
                #     testcase_node.set_field_value(
                #         field_name="TEST_FUNCTION",
                #         form_field_index=0,
                #         value=SDocNodeField(
                #             parent=testcase_node,
                #             field_name="TEST_FUNCTION",
                #             parts=[test_case_node_test_function],
                #             multiline__=None,
                #         ),
                #     )
                # testcase_node.set_field_value(
                #     field_name="DURATION",
                #     form_field_index=0,
                #     value=SDocNodeField(
                #         parent=testcase_node,
                #         field_name="DURATION",
                #         parts=[test_case_node_duration],
                #         multiline__=None,
                #     ),
                # )
                # testcase_node.set_field_value(
                #     field_name="STATUS",
                #     form_field_index=0,
                #     value=SDocNodeField(
                #         parent=testcase_node,
                #         field_name="STATUS",
                #         parts=[test_case_node_status],
                #         multiline__=None,
                #     ),
                # )
                testcase_node.set_field_value(
                    field_name="TITLE",
                    form_field_index=0,
                    value=SDocNodeField(
                        parent=testcase_node,
                        field_name="TITLE",
                        parts=[json_function_name],
                        multiline__=None,
                    ),
                )
                testcase_node.relations.append(
                    FileReference(
                        parent=testcase_node,
                        g_file_entry=FileEntry(
                            parent=None,
                            g_file_format=FileEntryFormat.SOURCECODE,
                            g_file_path=json_file_name,
                            g_line_range=None,
                            function=json_function_name,
                            clazz=None,
                        ),
                    )
                )
                file_section.section_contents.append(testcase_node)

        return document
