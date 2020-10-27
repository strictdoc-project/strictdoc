import os
import sys

from strictdoc.backend.dsl.reader import SDReader
from strictdoc.backend.dsl.writer import SDWriter


class PassthroughAction:

    def passthrough(self, path_to_doc, output_file):
        if not os.path.isfile(path_to_doc):
            sys.stdout.flush()
            err = "Could not open doc file '{}': No such file or directory".format(path_to_doc)
            print(err)
            exit(1)

        document = SDReader().read_from_file(path_to_doc)

        writer = SDWriter()
        output = writer.write(document)
        with open(output_file, 'w') as file:
            file.write(output)
