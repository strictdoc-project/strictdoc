from strictdoc.cli.cli_arg_parser import (
    SDocArgsParser,
)
from strictdoc.cli.main import COMMAND_REGISTRY

FAKE_STRICTDOC_ROOT_PATH = "/tmp/strictdoc-123"


def cli_args_parser():
    return SDocArgsParser.build_argparse(COMMAND_REGISTRY)


def test_export_01_minimal():
    parser = cli_args_parser()
    args = parser.parse_args(["export", "docs"])

    assert args.command == "export"
    assert args.debug is False
    assert args.fields == ["uid", "statement", "parent"]
    assert args.formats == ["html"]
    assert args.input_paths == ["docs"]
    assert args.no_parallelization is False
    assert args.output_dir is None
    assert args.enable_mathjax is False


def test_export_02_output_dir():
    parser = cli_args_parser()

    args = parser.parse_args(
        ["export", "docs", "--output-dir", "custom-output-dir"]
    )

    assert args.command == "export"
    assert args.input_paths == ["docs"]
    assert args.fields == ["uid", "statement", "parent"]
    assert args.formats == ["html"]
    assert args.no_parallelization is False
    assert args.output_dir == "custom-output-dir"


def test_export_03_parallelization():
    parser = cli_args_parser()

    args = parser.parse_args(["export", "docs", "--no-parallelization"])

    assert args.command == "export"
    assert args.fields == ["uid", "statement", "parent"]
    assert args.formats == ["html"]
    assert args.input_paths == ["docs"]
    assert args.no_parallelization is True
    assert args.output_dir is None


def test_export_04_export_format_rst():
    parser = cli_args_parser()

    args = parser.parse_args(["export", "--formats=rst", "docs"])

    assert args.command == "export"
    assert args.fields == ["uid", "statement", "parent"]
    assert args.formats == ["rst"]
    assert args.input_paths == ["docs"]
    assert args.no_parallelization is False
    assert args.output_dir is None


def test_export_05_export_format_multiple():
    parser = cli_args_parser()

    args = parser.parse_args(["export", "--formats=html,rst", "docs"])

    assert args.command == "export"
    assert args.input_paths == ["docs"]

    assert args.command == "export"
    assert args.fields == ["uid", "statement", "parent"]
    assert args.formats == ["html", "rst"]
    assert args.input_paths == ["docs"]
    assert args.no_parallelization is False
    assert args.output_dir is None


def test_export_06_export_format_markdown():
    parser = cli_args_parser()

    args = parser.parse_args(["export", "--formats=markdown", "docs"])

    assert args.command == "export"
    assert args.fields == ["uid", "statement", "parent"]
    assert args.formats == ["markdown"]
    assert args.input_paths == ["docs"]
    assert args.no_parallelization is False
    assert args.output_dir is None


def test_export_07_enable_mathjax():
    parser = cli_args_parser()
    args = parser.parse_args(["export", "--enable-mathjax", "docs"])

    assert args.command == "export"
    assert args.enable_mathjax is True


def test_export_08_project_title():
    parser = cli_args_parser()

    args = parser.parse_args(["export", "docs", "--project-title", "StrictDoc"])

    assert args.project_title == "StrictDoc"


def test_export_09_config():
    parser = cli_args_parser()

    args = parser.parse_args(
        ["export", "docs", "--config", "/path/to/strictdoc_config.py"]
    )
    assert args.command == "export"


def test_new_01_minimal():
    parser = cli_args_parser()

    args = parser.parse_args(["new", FAKE_STRICTDOC_ROOT_PATH])

    assert args.command == "new"
    assert args.input_path == FAKE_STRICTDOC_ROOT_PATH


def test_debug_flag_alone_does_not_imply_development_mode():
    """Regression: --debug must not, by itself, imply --development."""
    parser = cli_args_parser()
    args = parser.parse_args(["--debug", "export", "docs"])
    sdoc_args_parser = SDocArgsParser(args, COMMAND_REGISTRY)

    assert sdoc_args_parser.is_debug_mode() is True
    assert sdoc_args_parser.is_development_mode() is False


def test_development_flag_sets_development_mode_independently_of_debug():
    parser = cli_args_parser()
    args = parser.parse_args(["--development", "export", "docs"])
    sdoc_args_parser = SDocArgsParser(args, COMMAND_REGISTRY)

    assert sdoc_args_parser.is_debug_mode() is False
    assert sdoc_args_parser.is_development_mode() is True


def test_development_flag_is_hidden_from_help_text():
    parser = cli_args_parser()
    assert "--development" not in parser.format_help()
