import os

from strictdoc import STRICTDOC_ROOT_PATH
from strictdoc.cli.cli_arg_parser import ExportCommandConfig
from strictdoc.core.actions.export_action import ExportAction
from strictdoc.helpers.parallelizer import NullParallelizer

assert os.path.isabs(STRICTDOC_ROOT_PATH), f"{STRICTDOC_ROOT_PATH}"


class MainController:
    def __init__(self, path_to_sdoc_tree: str):
        self.path_to_sdoc_tree = path_to_sdoc_tree

        parallelizer = NullParallelizer()
        self.output_dir = os.path.join(self.path_to_sdoc_tree, "output")
        config = ExportCommandConfig(
            strictdoc_root_path=STRICTDOC_ROOT_PATH,
            input_paths=self.path_to_sdoc_tree,
            output_dir=self.output_dir,
            project_title="PROJECT_TITLE",
            formats=["html"],
            fields=None,
            no_parallelization=False,
            enable_mathjax=False,
            experimental_enable_file_traceability=False,
        )
        self.export_action = ExportAction(
            config=config, parallelizer=parallelizer
        )
        self.export_action.prepare()
        self.export_action.export()

    def get_document(self, path_to_document):
        full_path_to_document = os.path.join(
            self.output_dir, "html", path_to_document
        )
        assert os.path.isfile(full_path_to_document), f"{full_path_to_document}"
        with open(full_path_to_document, encoding="utf8") as sample_sdoc:
            content = sample_sdoc.read()
        return content
