import argparse


EXPORT_FORMATS = ["html", "html-standalone", "rst", "excel"]


def _check_formats(formats):
    formats_array = formats.split(",")
    for fmt in formats_array:
        if fmt in EXPORT_FORMATS:
            continue
        message = "invalid choice: '{}' (choose from {})".format(
            fmt, ", ".join(map(lambda f: "'{}'".format(f), EXPORT_FORMATS))
        )
        raise argparse.ArgumentTypeError(message)
    return formats_array


def _parse_fields(fields):
    fields_array = fields.split(",")
    return fields_array


def cli_args_parser() -> argparse.ArgumentParser:
    # for arg in sys.argv:
    #     if arg == '--help':
    #         # print_help()
    #         assert 0
    #         exit(0)
    #
    # for arg in sys.argv:
    #     if arg == '--version':
    #         # print_version()
    #         assert 0
    #         exit(0)

    # https://stackoverflow.com/a/19476216/598057
    main_parser = argparse.ArgumentParser()

    command_subparsers = main_parser.add_subparsers(
        title="command", dest="command"
    )
    command_subparsers.required = True

    command_parser_export = command_subparsers.add_parser(
        "export",
        help="Export document tree.",
        parents=[],
        description="Export command: input SDoc documents are generated into HTML and other formats.",
    )
    command_parser_export.add_argument(
        "input_paths",
        type=str,
        nargs="+",
        help="One or more folders with *.sdoc files",
    )
    command_parser_export.add_argument(
        "--output-dir", type=str, help="Output folder"
    )
    command_parser_export.add_argument(
        "--formats",
        type=_check_formats,
        default=["html"],
        help="Export fields, only used for Excel export",
    )
    command_parser_export.add_argument(
        "--fields",
        type=_parse_fields,
        default=["uid", "statement", "parent"],
        help="Export formats",
    )
    command_parser_export.add_argument(
        "--no-parallelization",
        action="store_true",
        help="Disables parallelization. All work happens in the main thread. This option might be useful for debugging.",
    )
    command_parser_export.add_argument(
        "--experimental-enable-file-traceability",
        action="store_true",
        help="Experimental feature: enables traceability between requirements and files (warning: implementation is not complete).",
    )

    command_parser_passthrough = command_subparsers.add_parser(
        "passthrough", help="Export document tree.", parents=[]
    )
    command_parser_passthrough.add_argument(
        "input_file", type=str, help="Path to the input SDoc file"
    )

    command_parser_passthrough.add_argument(
        "--output-file", type=str, help="Path to the output SDoc file"
    )

    return main_parser


class PassthroughCommandConfig:
    def __init__(self, input_file, output_file):
        self.input_file = input_file
        self.output_file = output_file


class ExportCommandConfig:
    def __init__(
        self,
        strictdoc_root_path,
        input_paths,
        output_dir,
        formats,
        fields,
        no_parallelization,
        experimental_enable_file_traceability,
    ):
        self.strictdoc_root_path = strictdoc_root_path
        self.input_paths = input_paths
        self.output_dir = output_dir
        self.formats = formats
        self.fields = fields
        self.no_parallelization = no_parallelization
        self.experimental_enable_file_traceability = (
            experimental_enable_file_traceability
        )


class SDocArgsParser:
    def __init__(self, args):
        self.args = args

    @property
    def is_passthrough_command(self):
        return self.args.command == "passthrough"

    def get_passthrough_config(self) -> PassthroughCommandConfig:
        return PassthroughCommandConfig(
            self.args.input_file, self.args.output_file
        )

    @property
    def is_export_command(self):
        return self.args.command == "export"

    def get_export_config(self, strictdoc_root_path) -> ExportCommandConfig:
        return ExportCommandConfig(
            strictdoc_root_path,
            self.args.input_paths,
            self.args.output_dir,
            self.args.formats,
            self.args.fields,
            self.args.no_parallelization,
            self.args.experimental_enable_file_traceability,
        )


def create_sdoc_args_parser(testing_args=None) -> SDocArgsParser:
    args = testing_args
    if not args:
        parser = cli_args_parser()
        args = parser.parse_args()
    return SDocArgsParser(args)
