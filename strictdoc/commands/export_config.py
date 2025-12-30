import os
from typing import List, Optional, Tuple

from strictdoc.cli.base_command import CLIValidationError
from strictdoc.helpers.auto_described import auto_described


@auto_described
class ExportCommandConfig:
    def __init__(
        self,
        *,
        debug: bool,
        command: str,
        input_paths: List[str],
        output_dir: Optional[str],
        config: Optional[str],
        project_title: Optional[str],
        formats: List[str],
        fields: List[str],
        generate_bundle_document: bool,
        no_parallelization: bool,
        enable_mathjax: bool,
        included_documents: bool,
        filter_nodes: Optional[str],
        reqif_profile: Optional[str],
        reqif_multiline_is_xhtml: bool,
        reqif_enable_mid: bool,
        view: Optional[str],
        generate_diff_git: Optional[str],
        generate_diff_dirs: Optional[Tuple[str, str]],
        chromedriver: Optional[str],
    ):
        assert isinstance(input_paths, list), f"{input_paths}"
        self.debug: bool = debug
        self.command: str = command
        self.input_paths: List[str] = input_paths
        self.output_dir: Optional[str] = output_dir
        self._config_path: Optional[str] = config
        self.project_title: Optional[str] = project_title
        self.formats: List[str] = formats
        self.fields: List[str] = fields
        self.generate_bundle_document: bool = generate_bundle_document
        self.no_parallelization: bool = no_parallelization
        self.enable_mathjax: bool = enable_mathjax
        self.included_documents: bool = included_documents
        self.filter_nodes: Optional[str] = filter_nodes
        self.reqif_profile: Optional[str] = reqif_profile
        self.reqif_multiline_is_xhtml: bool = reqif_multiline_is_xhtml
        self.reqif_enable_mid: bool = reqif_enable_mid
        self.view: Optional[str] = view
        self.generate_diff_git: Optional[str] = generate_diff_git
        self.generate_diff_dirs: Optional[Tuple[str, str]] = generate_diff_dirs
        self.chromedriver: Optional[str] = chromedriver

    def get_path_to_config(self) -> str:
        # FIXME: The control flow can be improved.
        path_to_input_dir: str = self.input_paths[0]
        if os.path.isfile(path_to_input_dir):
            path_to_input_dir = os.path.dirname(path_to_input_dir)
        path_to_config = (
            self._config_path
            if self._config_path is not None
            else path_to_input_dir
        )
        return path_to_config

    def validate(self) -> None:
        for idx_, input_path_ in enumerate(self.input_paths.copy()):
            if not os.path.exists(input_path_):
                raise CLIValidationError(
                    f"Provided input path does not exist: {input_path_}"
                )
            if not os.path.isabs(input_path_):
                self.input_paths[idx_] = os.path.abspath(input_path_).rstrip(
                    "/"
                )
        if self._config_path is not None:
            if not os.path.exists(self._config_path):
                raise CLIValidationError(
                    "Provided path to a configuration file does not exist: "
                    f"{self._config_path}"
                )
