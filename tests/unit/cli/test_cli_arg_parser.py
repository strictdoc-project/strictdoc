from strictdoc.cli.cli_arg_parser import cli_args_parser


STRICTDOC_CMD='strictdoc'


def test_export_01_minimal():
    parser = cli_args_parser()

    args = parser.parse_args(['export', 'docs'])

    assert args.command == 'export'
    assert args.input_file == ['docs']

    assert args._get_kwargs() == [('command', 'export'), ('input_file', ['docs'])]


def test_passthrough_01_minimal():
    parser = cli_args_parser()

    args = parser.parse_args(['passthrough', 'input.sdoc'])

    assert args._get_kwargs() == [('command', 'passthrough'),
                                  ('input_file', 'input.sdoc'),
                                  ('output_file', None)]


def test_passthrough_02_minimal():
    parser = cli_args_parser()

    args = parser.parse_args(['passthrough', 'input.sdoc', '--output-file', 'output.sdoc'])

    assert args._get_kwargs() == [('command', 'passthrough'),
                                  ('input_file', 'input.sdoc'),
                                  ('output_file', 'output.sdoc')]
