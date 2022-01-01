import os
import sys

from strictdoc.backend.sdoc.reader import SDReader
from strictdoc.backend.sdoc.writer import SDWriter
from strictdoc.cli.cli_arg_parser import PassthroughCommandConfig


class PassthroughAction:
    @staticmethod
    def passthrough(config: PassthroughCommandConfig):
        if not os.path.isfile(config.input_file):
            sys.stdout.flush()
            err = (
                f"Could not open doc file '{config.input_file}': "
                "No such file or directory"
            )
            print(err)
            sys.exit(1)

        document = SDReader().read_from_file(config.input_file)

        writer = SDWriter()
        output = writer.write(document)
        with open(config.output_file, "w", encoding="utf8") as file:
            file.write(output)
