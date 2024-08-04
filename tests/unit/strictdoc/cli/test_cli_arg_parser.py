import os

from strictdoc.cli.cli_arg_parser import (
    CommandParserBuilder,
    create_sdoc_args_parser,
)

FAKE_STRICTDOC_ROOT_PATH = "/tmp/strictdoc-123"


TOTAL_EXPORT_ARGS = 18


def cli_args_parser():
    return CommandParserBuilder().build()


def test_export_01_minimal():
    parser = cli_args_parser()
    args = parser.parse_args(["export", "docs"])

    assert len(args._get_kwargs()) == TOTAL_EXPORT_ARGS

    assert args.command == "export"
    assert args.fields == ["uid", "statement", "parent"]
    assert args.formats == ["html"]
    assert args.input_paths == ["docs"]
    assert args.no_parallelization is False
    assert args.output_dir is None
    assert args.enable_mathjax is False

    config_parser = create_sdoc_args_parser(args)
    export_config = config_parser.get_export_config()
    assert export_config.fields == args.fields
    assert export_config.formats == args.formats
    assert export_config.input_paths == args.input_paths
    # When no explicit --config path provided, the path to config defaults to
    # the input path.
    assert export_config.get_path_to_config() == "docs"
    assert export_config.no_parallelization == args.no_parallelization
    assert export_config.output_dir == os.path.join(os.getcwd(), "output")


def test_export_02_output_dir():
    parser = cli_args_parser()

    args = parser.parse_args(
        ["export", "docs", "--output-dir", "custom-output-dir"]
    )

    assert len(args._get_kwargs()) == TOTAL_EXPORT_ARGS

    assert args.command == "export"
    assert args.input_paths == ["docs"]
    assert args.fields == ["uid", "statement", "parent"]
    assert args.formats == ["html"]
    assert args.no_parallelization is False
    assert args.output_dir == "custom-output-dir"

    config_parser = create_sdoc_args_parser(args)
    export_config = config_parser.get_export_config()
    assert export_config.fields == args.fields
    assert export_config.formats == args.formats
    assert export_config.input_paths == args.input_paths
    assert export_config.no_parallelization == args.no_parallelization
    assert export_config.output_dir == os.path.join(
        os.getcwd(), "custom-output-dir"
    )


def test_export_03_parallelization():
    parser = cli_args_parser()

    args = parser.parse_args(["export", "docs", "--no-parallelization"])

    assert len(args._get_kwargs()) == TOTAL_EXPORT_ARGS

    assert args.command == "export"
    assert args.fields == ["uid", "statement", "parent"]
    assert args.formats == ["html"]
    assert args.input_paths == ["docs"]
    assert args.no_parallelization is True
    assert args.output_dir is None

    config_parser = create_sdoc_args_parser(args)
    export_config = config_parser.get_export_config()
    assert export_config.fields == args.fields
    assert export_config.formats == args.formats
    assert export_config.input_paths == args.input_paths
    assert export_config.no_parallelization == args.no_parallelization


def test_export_04_export_format_rst():
    parser = cli_args_parser()

    args = parser.parse_args(["export", "--formats=rst", "docs"])

    assert len(args._get_kwargs()) == TOTAL_EXPORT_ARGS

    assert args.command == "export"
    assert args.fields == ["uid", "statement", "parent"]
    assert args.formats == ["rst"]
    assert args.input_paths == ["docs"]
    assert args.no_parallelization is False
    assert args.output_dir is None

    config_parser = create_sdoc_args_parser(args)
    export_config = config_parser.get_export_config()
    assert export_config.fields == args.fields
    assert export_config.formats == args.formats
    assert export_config.input_paths == args.input_paths
    assert export_config.no_parallelization == args.no_parallelization


def test_export_05_export_format_multiple():
    parser = cli_args_parser()

    args = parser.parse_args(["export", "--formats=html,rst", "docs"])

    assert args.command == "export"
    assert args.input_paths == ["docs"]

    assert len(args._get_kwargs()) == TOTAL_EXPORT_ARGS

    assert args.command == "export"
    assert args.fields == ["uid", "statement", "parent"]
    assert args.formats == ["html", "rst"]
    assert args.input_paths == ["docs"]
    assert args.no_parallelization is False
    assert args.output_dir is None

    config_parser = create_sdoc_args_parser(args)
    export_config = config_parser.get_export_config()
    assert export_config.fields == args.fields
    assert export_config.formats == args.formats
    assert export_config.input_paths == args.input_paths
    assert export_config.no_parallelization == args.no_parallelization


def test_export_07_enable_mathjax():
    parser = cli_args_parser()
    args = parser.parse_args(["export", "--enable-mathjax", "docs"])

    assert len(args._get_kwargs()) == TOTAL_EXPORT_ARGS

    assert args.command == "export"
    assert args.enable_mathjax is True

    config_parser = create_sdoc_args_parser(args)
    export_config = config_parser.get_export_config()
    assert export_config.enable_mathjax is True


def test_export_08_project_title():
    parser = cli_args_parser()

    args = parser.parse_args(["export", "docs", "--project-title", "StrictDoc"])

    assert len(args._get_kwargs()) == TOTAL_EXPORT_ARGS
    assert args.project_title == "StrictDoc"

    config_parser = create_sdoc_args_parser(args)
    export_config = config_parser.get_export_config()
    assert export_config.project_title == args.project_title


def test_export_09_config():
    parser = cli_args_parser()

    args = parser.parse_args(
        ["export", "docs", "--config", "/path/to/strictdoc.toml"]
    )

    assert len(args._get_kwargs()) == TOTAL_EXPORT_ARGS

    config_parser = create_sdoc_args_parser(args)
    export_config = config_parser.get_export_config()
    assert export_config.get_path_to_config() == "/path/to/strictdoc.toml"


def test_passthrough_01_minimal():
    parser = cli_args_parser()

    args = parser.parse_args(["passthrough", "input.sdoc"])

    assert sorted(args._get_kwargs()) == [
        ("command", "passthrough"),
        ("filter_requirements", None),
        ("filter_sections", None),
        ("free_text_to_text", False),
        ("input_file", "input.sdoc"),
        ("output_dir", None),
        ("view", None),
    ]


def test_passthrough_02_minimal():
    parser = cli_args_parser()

    args = parser.parse_args(
        ["passthrough", "input.sdoc", "--output-dir", "SANDBOX/"]
    )

    assert sorted(args._get_kwargs()) == [
        ("command", "passthrough"),
        ("filter_requirements", None),
        ("filter_sections", None),
        ("free_text_to_text", False),
        ("input_file", "input.sdoc"),
        ("output_dir", "SANDBOX/"),
        ("view", None),
    ]
