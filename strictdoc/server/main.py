import argparse
import os
import sys

from strictdoc.cli.cli_arg_parser import ServerCommandConfig
from strictdoc.server.server import run_strictdoc_server

try:
    strictdoc_path = os.path.abspath(os.path.join(__file__, "../../.."))
    assert os.path.exists(strictdoc_path), f"does not exist: {strictdoc_path}"
    sys.path.append(strictdoc_path)
except AssertionError:
    print("Cannot find strictdoc's root folder.")
    sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input_path")
    parser.add_argument(
        "output_path", type=str, default="/tmp/strictdoc/output"
    )

    parser.add_argument("--reload", default=True, action="store_true")
    parser.add_argument("--no-reload", dest="reload", action="store_false")
    args = parser.parse_args()

    input_path = args.input_path
    assert os.path.exists(input_path)
    output_path = args.output_path
    assert os.path.exists(output_path)

    server_command_config = ServerCommandConfig(
        input_path=input_path, output_path=output_path, reload=args.reload
    )
    run_strictdoc_server(config=server_command_config)
