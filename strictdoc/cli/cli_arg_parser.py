import argparse


def cli_args_parser():
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

    # if os.path.getsize(check_file) == 0:
    #     sys.stdout.flush()
    #     print("error: no check strings found with prefix 'CHECK:'", file=sys.stderr)
    #     exit(2)

    # https://stackoverflow.com/a/19476216/598057
    main_parser = argparse.ArgumentParser()

    command_subparsers = main_parser.add_subparsers(title="command",
                                                    dest="command")
    command_subparsers.required = True

    command_parser_export = command_subparsers.add_parser(
        "export",
        help="Export document tree.",
        parents=[],
        description="Export command: input SDoc documents are generated into HTML and other formats."
    )
    command_parser_export.add_argument('input_paths',
                                        type=str,
                                        nargs='+',
                                        help='One or more folders with *.sdoc files')
    command_parser_export.add_argument('--output-dir',
                                       type=str,
                                       help='Output folder')
    command_parser_export.add_argument('--no-parallelization',
                                       action='store_true',
                                       help='Disables parallelization. All work happens in the main thread. This option might be useful for debugging.')

    command_parser_passthrough = command_subparsers.add_parser(
        "passthrough", help="Export document tree.", parents=[]
    )
    command_parser_passthrough.add_argument('input_file',
                                            type=str,
                                            help='Path to the input SDoc file')

    command_parser_passthrough.add_argument('--output-file',
                                            type=str,
                                            help='Path to the output SDoc file')

    return main_parser
