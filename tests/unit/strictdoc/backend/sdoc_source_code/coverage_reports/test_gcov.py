import hashlib
from types import SimpleNamespace

from strictdoc.backend.gcov.reader import (
    GCovJSONReader,
)


def test_gcov_html_link_uses_actual_source_file_path_for_hash():
    document = GCovJSONReader.read_from_string(
        """
        {
          "files": [
            {
              "file": "src/functions.cpp",
              "functions": [
                {
                  "demangled_name": "test::Adder::add(int const&, int const&)",
                  "execution_count": 1
                }
              ]
            }
          ]
        }
        """,
        doc_file=None,  # type: ignore[arg-type]
        project_config=None,  # type: ignore[arg-type]
    )

    source_path_hash = hashlib.md5(b"src/functions.cpp").hexdigest()
    testcase_node = (
        document.section_contents[1].section_contents[1].section_contents[0]
    )
    statement = testcase_node.get_field_by_name("STATEMENT").parts[0]

    assert f"coverage.functions.cpp. {source_path_hash}.html" in statement


def test_gcov_report_normalizes_windows_source_file_path():
    document = GCovJSONReader.read_from_string(
        """
        {
          "files": [
            {
              "file": "src\\\\functions.cpp",
              "functions": [
                {
                  "demangled_name": "test::Adder::add(int const&, int const&)",
                  "execution_count": 1
                }
              ]
            }
          ]
        }
        """,
        doc_file=None,  # type: ignore[arg-type]
        project_config=None,  # type: ignore[arg-type]
    )

    source_path_hash = hashlib.md5(b"src/functions.cpp").hexdigest()
    testcase_node = (
        document.section_contents[1].section_contents[1].section_contents[0]
    )
    statement = testcase_node.get_field_by_name("STATEMENT").parts[0]
    uid = testcase_node.reserved_uid
    file_reference = testcase_node.relations[0]

    assert uid == (
        "GCOV:src/functions.cpp:test::Adder::add(int const&, int const&)"
    )
    assert file_reference.g_file_entry.g_file_path == "src/functions.cpp"
    assert f"coverage.functions.cpp. {source_path_hash}.html" in statement


def test_gcov_report_relativizes_windows_absolute_source_file_path():
    document = GCovJSONReader.read_from_string(
        """
        {
          "files": [
            {
              "file": "D:\\\\a\\\\strictdoc\\\\strictdoc\\\\docs\\\\src\\\\functions.cpp",
              "functions": [
                {
                  "demangled_name": "test::Adder::add(int const&, int const&)",
                  "execution_count": 1
                }
              ]
            }
          ]
        }
        """,
        doc_file=None,  # type: ignore[arg-type]
        project_config=SimpleNamespace(
            source_root_path="D:\\a\\strictdoc\\strictdoc\\docs"
        ),  # type: ignore[arg-type]
    )

    source_path_hash = hashlib.md5(b"src/functions.cpp").hexdigest()
    testcase_node = (
        document.section_contents[1].section_contents[1].section_contents[0]
    )
    statement = testcase_node.get_field_by_name("STATEMENT").parts[0]
    uid = testcase_node.reserved_uid
    file_reference = testcase_node.relations[0]

    assert uid == (
        "GCOV:src/functions.cpp:test::Adder::add(int const&, int const&)"
    )
    assert file_reference.g_file_entry.g_file_path == "src/functions.cpp"
    assert f"coverage.functions.cpp. {source_path_hash}.html" in statement


def test_gcov_report_prefers_demangled_name_over_name():
    document = GCovJSONReader.read_from_string(
        """
        {
          "files": [
            {
              "file": "src/functions.cpp",
              "functions": [
                {
                  "name": "_ZN4test5Adder3addERKiS2_",
                  "demangled_name": "test::Adder::add(int const&, int const&)",
                  "execution_count": 1
                }
              ]
            }
          ]
        }
        """,
        doc_file=None,  # type: ignore[arg-type]
        project_config=None,  # type: ignore[arg-type]
    )

    testcase_node = (
        document.section_contents[1].section_contents[1].section_contents[0]
    )

    assert testcase_node.reserved_uid == (
        "GCOV:src/functions.cpp:test::Adder::add(int const&, int const&)"
    )
    assert testcase_node.get_field_by_name("TITLE").parts[0] == (
        "test::Adder::add(int const&, int const&)"
    )
    assert testcase_node.relations[0].g_file_entry.id == (
        "test::Adder::add(int const&, int const&)"
    )
