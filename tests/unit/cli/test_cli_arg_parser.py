from strictdoc.cli.cli_arg_parser import (
    cli_args_parser,
    create_sdoc_args_parser,
)

STRICTDOC_CMD = "strictdoc"


TOTAL_EXPORT_ARGS = 7


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

    config_parser = create_sdoc_args_parser(args)
    export_config = config_parser.get_export_config()
    assert export_config.fields == args.fields
    assert export_config.formats == args.formats
    assert export_config.input_paths == args.input_paths
    assert export_config.no_parallelization == args.no_parallelization
    assert export_config.output_dir == args.output_dir


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
    assert export_config.output_dir == args.output_dir


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
    assert export_config.output_dir == args.output_dir


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
    assert export_config.output_dir == args.output_dir


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


def test_export_06_export_format_multiple():
    parser = cli_args_parser()

    args = parser.parse_args(
        ["export", "--experimental-enable-file-traceability", "docs"]
    )

    assert args.command == "export"
    assert args.input_paths == ["docs"]

    assert len(args._get_kwargs()) == TOTAL_EXPORT_ARGS
    assert args.command == "export"
    assert args.experimental_enable_file_traceability is True

    config_parser = create_sdoc_args_parser(args)
    export_config = config_parser.get_export_config()
    assert export_config.fields == args.fields
    assert export_config.formats == args.formats
    assert export_config.input_paths == args.input_paths
    assert export_config.no_parallelization == args.no_parallelization
    assert export_config.output_dir == args.output_dir


def test_passthrough_01_minimal():
    parser = cli_args_parser()

    args = parser.parse_args(["passthrough", "input.sdoc"])

    assert args._get_kwargs() == [
        ("command", "passthrough"),
        ("input_file", "input.sdoc"),
        ("output_file", None),
    ]


def test_passthrough_02_minimal():
    parser = cli_args_parser()

    args = parser.parse_args(
        ["passthrough", "input.sdoc", "--output-file", "output.sdoc"]
    )

    assert args._get_kwargs() == [
        ("command", "passthrough"),
        ("input_file", "input.sdoc"),
        ("output_file", "output.sdoc"),
    ]
