import os
import sys

from strictdoc.backend.dsl.reader import SDReader
from strictdoc.backend.dsl.writer import SDWriter
from strictdoc.cli.cli_arg_parser import PassthroughCommandConfig


class PassthroughAction:
    def passthrough(self, config: PassthroughCommandConfig):
        if not os.path.isfile(config.input_file):
            sys.stdout.flush()
            err = "Could not open doc file '{}': No such file or directory".format(
                config.input_file
            )
            print(err)
            exit(1)

        document = SDReader().read_from_file(config.input_file)

        writer = SDWriter()
        output = writer.write(document)
        with open(config.output_file, "w") as file:
            file.write(output)
