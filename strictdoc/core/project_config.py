"""
@relation(SDOC-SRS-39, scope=file)
"""

import datetime
import os
import re
import tempfile
import types
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import toml

from strictdoc import __version__, environment
from strictdoc.backend.reqif.sdoc_reqif_fields import ReqIFProfile
from strictdoc.backend.sdoc.constants import SDocMarkup
from strictdoc.commands.export_config import ExportCommandConfig
from strictdoc.commands.import_excel_config import ImportExcelCommandConfig
from strictdoc.commands.import_reqif_config import ImportReqIFCommandConfig
from strictdoc.commands.manage_autouid_config import ManageAutoUIDCommandConfig
from strictdoc.commands.server_config import ServerCommandConfig
from strictdoc.core.environment import SDocRuntimeEnvironment
from strictdoc.core.plugin import StrictDocPlugin
from strictdoc.helpers.auto_described import auto_described
from strictdoc.helpers.deprecation_engine import DEPRECATION_ENGINE
from strictdoc.helpers.exception import StrictDocException
from strictdoc.helpers.file_modification_time import get_file_modification_time
from strictdoc.helpers.md5 import get_md5
from strictdoc.helpers.module import import_from_path
from strictdoc.helpers.net import is_valid_host
from strictdoc.helpers.path_filter import validate_mask


def parse_relation_tuple(column_name: str) -> Optional[Tuple[str, str]]:
    match_result = re.search(
        r"^((Parent|Child|File)?)(\[(.{1,32})])?$", column_name
    )
    if match_result is None:
        return None
    return match_result.group(1), match_result.group(4)


@dataclass
class SourceNodesEntry:
    path: str
    uid: str
    node_type: str
    sdoc_to_source_map: Dict[str, str] = field(default_factory=dict)
    full_path: Optional[Path] = None


class ProjectFeature(str, Enum):
    # Stable features.
    TABLE_SCREEN = "TABLE_SCREEN"
    TRACEABILITY_SCREEN = "TRACEABILITY_SCREEN"
    DEEP_TRACEABILITY_SCREEN = "DEEP_TRACEABILITY_SCREEN"

    MATHJAX = "MATHJAX"

    # Experimental features.
    SEARCH = "SEARCH"
    HTML2PDF = "HTML2PDF"
    REQIF = "REQIF"
    DIFF = "DIFF"
    PROJECT_STATISTICS_SCREEN = "PROJECT_STATISTICS_SCREEN"
    TREE_MAP_SCREEN = "TREE_MAP_SCREEN"
    STANDALONE_DOCUMENT_SCREEN = "STANDALONE_DOCUMENT_SCREEN"
    TRACEABILITY_MATRIX_SCREEN = "TRACEABILITY_MATRIX_SCREEN"
    REQUIREMENT_TO_SOURCE_TRACEABILITY = "REQUIREMENT_TO_SOURCE_TRACEABILITY"
    SOURCE_FILE_LANGUAGE_PARSERS = "SOURCE_FILE_LANGUAGE_PARSERS"

    MERMAID = "MERMAID"
    RAPIDOC = "RAPIDOC"
    NESTOR = "NESTOR"

    ALL_FEATURES = "ALL_FEATURES"

    @staticmethod
    def all() -> List[str]:  # noqa: A003
        return list(map(lambda c: c.value, ProjectFeature))


class ProjectConfigDefault:
    DEFAULT_PROJECT_TITLE = "Untitled Project"
    DEFAULT_DIR_FOR_SDOC_ASSETS = "_static"
    DEFAULT_DIR_FOR_OUTPUT = "output"
    DEFAULT_DIR_FOR_SDOC_CACHE = "output/_cache"

    DEFAULT_FEATURES: List[str] = [
        ProjectFeature.TABLE_SCREEN,
        ProjectFeature.TRACEABILITY_SCREEN,
        ProjectFeature.DEEP_TRACEABILITY_SCREEN,
        ProjectFeature.SEARCH,
    ]
    DEFAULT_SERVER_HOST = "127.0.0.1"
    DEFAULT_SERVER_PORT = 5111
    DEFAULT_BUNDLE_DOCUMENT_VERSION = "@GIT_VERSION (Git branch: @GIT_BRANCH)"
    DEFAULT_BUNDLE_DOCUMENT_COMMIT_DATE = "@GIT_COMMIT_DATETIME"
    DEFAULT_SECTION_BEHAVIOR = "[SECTION]"


@auto_described
class ProjectConfig:
    """
    @relation(SDOC-SRS-119, scope=class)
    """

    def __init__(
        self,
        project_title: str = ProjectConfigDefault.DEFAULT_PROJECT_TITLE,
        dir_for_sdoc_assets: str = ProjectConfigDefault.DEFAULT_DIR_FOR_SDOC_ASSETS,
        dir_for_sdoc_cache: str = ProjectConfigDefault.DEFAULT_DIR_FOR_SDOC_CACHE,
        project_features: Optional[List[str]] = None,
        server_host: str = ProjectConfigDefault.DEFAULT_SERVER_HOST,
        server_port: int = ProjectConfigDefault.DEFAULT_SERVER_PORT,
        input_paths: Optional[List[str]] = None,
        include_doc_paths: Optional[List[str]] = None,
        exclude_doc_paths: Optional[List[str]] = None,
        source_root_path: Optional[str] = None,
        include_source_paths: Optional[List[str]] = None,
        exclude_source_paths: Optional[List[str]] = None,
        grammars: Optional[Dict[str, str]] = None,
        test_report_root_dict: Optional[Dict[str, str]] = None,
        source_nodes: Optional[List[SourceNodesEntry]] = None,
        html2pdf_strict: bool = False,
        html2pdf_template: Optional[str] = None,
        html2pdf_forced_page_break_nodes: Optional[List[str]] = None,
        bundle_document_uid: Optional[str] = None,
        bundle_document_version: Optional[
            str
        ] = ProjectConfigDefault.DEFAULT_BUNDLE_DOCUMENT_VERSION,
        bundle_document_date: Optional[
            str
        ] = ProjectConfigDefault.DEFAULT_BUNDLE_DOCUMENT_COMMIT_DATE,
        traceability_matrix_relation_columns: Optional[
            List[Tuple[str, Optional[str]]]
        ] = None,
        reqif_profile: str = ReqIFProfile.P01_SDOC,
        # FIXME: Change to true by default.
        reqif_multiline_is_xhtml: bool = False,
        # FIXME: Change to true by default.
        reqif_enable_mid: bool = False,
        reqif_import_markup: Optional[str] = None,
        diff_git_revisions: Optional[str] = None,
        diff_dir_revisions: Optional[Tuple[str, str]] = None,
        chromedriver: Optional[str] = None,
        # FIXME: The section_behavior field will be removed by the end of 2025-Q4.
        section_behavior: Optional[
            str
        ] = ProjectConfigDefault.DEFAULT_SECTION_BEHAVIOR,
        statistics_generator: Optional[str] = None,
        user_plugin: Optional[StrictDocPlugin] = None,
        # Reserved for StrictDoc's internal use.
        _config_last_update: Optional[datetime.datetime] = None,
    ) -> None:
        self.environment: SDocRuntimeEnvironment = environment

        # Settings obtained from the strictdoc.toml config file.
        self.project_title: str = project_title
        self.dir_for_sdoc_assets: str = dir_for_sdoc_assets

        if env_cache_dir := os.environ.get("STRICTDOC_CACHE_DIR"):
            # The only use case for STRICTDOC_CACHE_DIR is to make the cache
            # local to an itest folder.
            assert env_cache_dir == "Output/_cache", env_cache_dir
            dir_for_sdoc_cache = env_cache_dir
        elif dir_for_sdoc_cache == "$TMPDIR":
            dir_for_sdoc_cache = os.path.join(
                tempfile.gettempdir(),
                "strictdoc_cache",
                get_md5(os.getcwd()),
            )

        # Adding a __version__ part to the cache directory improves traceability
        # by indicating which StrictDoc version the cache belongs to.
        # This helps prevent issues when switching between versions that may use
        # incompatible cache schemas.
        dir_for_sdoc_cache = os.path.join(dir_for_sdoc_cache, __version__)

        self.dir_for_sdoc_cache: str = dir_for_sdoc_cache

        #
        # project_features
        #
        project_features = (
            project_features
            if project_features is not None
            else ProjectConfigDefault.DEFAULT_FEATURES
        )

        assert isinstance(project_features, list), (
            f"config: project_features: parameter must be an "
            f"array: '{project_features}'."
        )

        for feature in project_features:
            assert feature in ProjectFeature.all(), (
                f"config: project_features: unknown feature declared: "
                f"'{feature}'."
            )

        if ProjectFeature.ALL_FEATURES in project_features:
            project_features = ProjectFeature.all()

        self.project_features: List[str] = project_features

        #
        # server_host and server_port
        #
        assert is_valid_host(server_host), (
            f"config: server_host: invalid host: {server_host}'."
        )
        self.server_host: str = server_host

        assert isinstance(server_port, int) and 1024 < server_port < 65000, (
            f"strictdoc.toml: 'port': invalid port: {server_port}'."
        )
        self.server_port: int = server_port

        #
        # input_paths
        #
        self.input_paths: Optional[List[str]] = input_paths

        #
        # include_doc_paths
        #
        include_doc_paths = include_doc_paths or []
        assert isinstance(include_doc_paths, list), include_doc_paths
        for include_doc_path in include_doc_paths:
            try:
                validate_mask(include_doc_path)
            except SyntaxError as exception_:
                raise ValueError(
                    f"config: include_doc_paths: {exception_}"
                ) from exception_
        self.include_doc_paths: List[str] = include_doc_paths

        #
        # exclude_doc_paths
        #
        exclude_doc_paths = exclude_doc_paths or []
        assert isinstance(exclude_doc_paths, list), exclude_doc_paths
        for exclude_doc_path in exclude_doc_paths:
            try:
                validate_mask(exclude_doc_path)
            except SyntaxError as exception_:
                raise ValueError(
                    f"config: exclude_doc_paths: {exception_}"
                ) from exception_
        self.exclude_doc_paths: List[str] = exclude_doc_paths

        #
        # include_source_paths
        #
        include_source_paths = include_source_paths or []
        assert isinstance(include_source_paths, list), include_source_paths
        for include_source_path in include_source_paths:
            try:
                validate_mask(include_source_path)
            except SyntaxError as exception_:
                raise ValueError(
                    f"config: include_source_paths: {exception_}"
                ) from exception_
        self.include_source_paths: List[str] = include_source_paths

        #
        # exclude_source_paths
        #
        exclude_source_paths = exclude_source_paths or []
        assert isinstance(exclude_source_paths, list), exclude_source_paths
        for exclude_source_path in exclude_source_paths:
            try:
                validate_mask(exclude_source_path)
            except SyntaxError as exception_:
                raise ValueError(
                    f"config: exclude_source_paths: {exception_}"
                ) from exception_
        self.exclude_source_paths: List[str] = exclude_source_paths

        #
        # source_root_path
        #
        self.source_root_path: Optional[str] = source_root_path

        #
        # grammars - Grammar aliases.
        #
        self.grammars: Dict[str, str] = grammars or {}

        self.test_report_root_dict: Dict[str, str] = (
            test_report_root_dict if test_report_root_dict is not None else {}
        )
        self.source_nodes: List[SourceNodesEntry] = (
            source_nodes if source_nodes is not None else []
        )

        # Settings derived from the command-line parameters.

        # Common settings.
        self.output_dir: str = ProjectConfigDefault.DEFAULT_DIR_FOR_OUTPUT

        # Export action.
        self.export_output_html_root: str = os.path.join(
            self.output_dir, "html"
        )
        self.export_formats: Optional[List[str]] = None
        self.export_included_documents: bool = False
        self.generate_bundle_document: bool = False
        self.filter_nodes: Optional[str] = None

        self.excel_export_fields: Optional[List[str]] = None

        assert isinstance(html2pdf_strict, bool), (
            "config: html2pdf_strict: "
            f"must be a True/False value: {html2pdf_strict}."
        )
        self.html2pdf_strict: bool = html2pdf_strict

        self.html2pdf_template: Optional[str] = html2pdf_template

        if html2pdf_forced_page_break_nodes is not None:
            assert isinstance(html2pdf_forced_page_break_nodes, list)
            assert len(html2pdf_forced_page_break_nodes) <= 10
        self.html2pdf_forced_page_break_nodes: List[str] = (
            html2pdf_forced_page_break_nodes or []
        )

        self.bundle_document_uid: Optional[str] = bundle_document_uid
        self.bundle_document_version: Optional[str] = bundle_document_version
        self.bundle_document_date: Optional[str] = bundle_document_date

        self.traceability_matrix_relation_columns: Optional[
            List[Tuple[str, Optional[str]]]
        ] = traceability_matrix_relation_columns

        #
        # ReqIF
        #
        self.reqif_profile: str = reqif_profile

        assert isinstance(reqif_multiline_is_xhtml, bool), (
            reqif_multiline_is_xhtml
        )
        self.reqif_multiline_is_xhtml: bool = reqif_multiline_is_xhtml

        assert isinstance(reqif_enable_mid, bool), reqif_enable_mid
        self.reqif_enable_mid: bool = reqif_enable_mid

        if reqif_import_markup is not None:
            assert reqif_import_markup in SDocMarkup.ALL, (
                "config: reqif_import_markup: expected a valid markup: "
                f"({SDocMarkup.ALL}). Got: "
                f"'{reqif_import_markup}'."
            )

        self.reqif_import_markup: Optional[str] = reqif_import_markup

        #
        # auto_uid_mode: default is False. The True-case is used by the
        # manage/auto_uid command: the SDocNodeValidator will
        # not raise an exception if it sees a node with a missing UID.
        # Important for a special case:
        # The Manage UID command auto-generates the UID, so the field presence
        # validation has to be relaxed.
        # The GitHub issue report:
        # manage auto-uid: UID field REQUIRED True leads to an error
        # https://github.com/strictdoc-project/strictdoc/issues/1896
        #
        self.auto_uid_mode = False
        self.autouuid_include_sections: bool = False

        self.view: Optional[str] = None

        self.diff_git_revisions: Optional[str] = diff_git_revisions
        self.diff_dir_revisions: Optional[Tuple[str, str]] = diff_dir_revisions

        self.chromedriver: Optional[str] = chromedriver
        self.section_behavior: Optional[str] = section_behavior

        self.statistics_generator: Optional[str] = statistics_generator
        self.user_plugin: Optional[StrictDocPlugin] = user_plugin

        self.config_last_update: Optional[datetime.datetime] = (
            _config_last_update
        )
        self.is_running_on_server: bool = False

    @staticmethod
    def default_config() -> "ProjectConfig":
        return ProjectConfig()

    # Some server command settings can override the project config settings.
    def integrate_server_config(
        self, server_config: ServerCommandConfig
    ) -> None:
        self.is_running_on_server = True
        if (server_host_ := server_config.host) is not None:
            self.server_host = server_host_
        if (server_port_ := server_config.port) is not None:
            self.server_port = server_port_

        self.input_paths = [server_config.get_full_input_path()]
        if self.source_root_path is None:
            source_root_path = self.input_paths[0]
            # If the input argument is a relative path, convert it to an
            # absolute path.
            source_root_path = os.path.abspath(source_root_path)
            source_root_path = source_root_path.rstrip("/")
            self.source_root_path = source_root_path

        # When setting the output dir, the CLI argument takes precedence.
        output_dir = self.output_dir
        if server_config.output_path is not None:
            output_dir = server_config.output_path
        elif output_dir == ProjectConfigDefault.DEFAULT_DIR_FOR_OUTPUT:
            output_dir = "./output/server"
        self.output_dir = output_dir

        self.export_output_html_root = os.path.join(output_dir, "html")

        # If a custom cache folder is not specified in the config, adjust the
        # cache folder to be located in the output folder.
        if self.dir_for_sdoc_cache.startswith(
            ProjectConfigDefault.DEFAULT_DIR_FOR_SDOC_CACHE
        ):
            self.dir_for_sdoc_cache = os.path.join(
                output_dir, "_cache", __version__
            )

        self.export_formats = ["html"]
        self.generate_bundle_document = False
        self.export_included_documents = True

    def integrate_export_config(
        self, export_config: ExportCommandConfig
    ) -> None:
        if export_config.project_title is not None:
            self.project_title = export_config.project_title

        self.input_paths = export_config.input_paths
        if self.source_root_path is None:
            source_root_path = export_config.input_paths[0]
            # If the input argument is a relative path, convert it to an
            # absolute path.
            source_root_path = os.path.abspath(source_root_path)
            source_root_path = source_root_path.rstrip("/")
            self.source_root_path = source_root_path

        #
        # Adjust the default output dir to the user-provided dir if needed.
        #
        output_dir = self.output_dir
        if export_config.output_dir is not None:
            output_dir = export_config.output_dir
        if not os.path.isabs(output_dir):
            cwd = os.getcwd()
            output_dir = os.path.join(cwd, output_dir)
        self.output_dir = output_dir

        # If a custom cache folder is not specified in the config, adjust the
        # cache folder to be located in the output folder.
        if self.dir_for_sdoc_cache.startswith(
            ProjectConfigDefault.DEFAULT_DIR_FOR_SDOC_CACHE
        ):
            self.dir_for_sdoc_cache = os.path.join(
                output_dir, "_cache", __version__
            )

        self.export_output_html_root = os.path.join(self.output_dir, "html")
        self.export_formats = export_config.formats
        self.export_included_documents = export_config.included_documents
        self.generate_bundle_document = export_config.generate_bundle_document
        self.filter_nodes = export_config.filter_nodes
        self.excel_export_fields = export_config.fields
        self.view = export_config.view

        if ProjectFeature.DIFF in self.project_features:
            if export_config.generate_diff_git is not None:
                self.diff_git_revisions = export_config.generate_diff_git
            if export_config.generate_diff_dirs is not None:
                self.diff_dir_revisions = export_config.generate_diff_dirs

        self.chromedriver = export_config.chromedriver

        if (
            export_config.enable_mathjax
            and ProjectFeature.MATHJAX not in self.project_features
        ):
            self.project_features.append(ProjectFeature.MATHJAX)

        if export_config.reqif_profile is not None:
            self.reqif_profile = export_config.reqif_profile

        # If the TOML file sets this to True, ignore what is in CLI.
        if not self.reqif_multiline_is_xhtml:
            self.reqif_multiline_is_xhtml = (
                export_config.reqif_multiline_is_xhtml
            )
        if not self.reqif_enable_mid:
            self.reqif_enable_mid = export_config.reqif_enable_mid

    def validate_and_finalize(self) -> None:
        project_path = self.get_project_root_path()

        #
        # Validate source nodes config.
        #
        if len(self.source_nodes) > 0 and not {
            ProjectFeature.REQUIREMENT_TO_SOURCE_TRACEABILITY,
            ProjectFeature.SOURCE_FILE_LANGUAGE_PARSERS,
        }.issubset(self.project_features):
            print(  # noqa: T201
                "warning: defining source_nodes without enabling REQUIREMENT_TO_SOURCE_TRACEABILITY and "
                "SOURCE_FILE_LANGUAGE_PARSERS has no effect"
            )

        #
        # Validate HTML2PDF template path.
        #
        if (html2pdf_template := self.html2pdf_template) is not None:
            assert not os.path.isabs(html2pdf_template)
            if project_path is not None:
                html2pdf_template = os.path.join(
                    project_path, html2pdf_template
                )
            if not os.path.isfile(html2pdf_template):
                raise ValueError(
                    "config: html2pdf_template: "
                    f"invalid path to a template file: {html2pdf_template}."
                )

        #
        # Validate path to Chrome Driver.
        #
        if (
            chromedriver := self.chromedriver
        ) is not None and not os.path.isfile(chromedriver):
            raise ValueError(
                f"config: chromedriver: not found at path: {chromedriver}."
            )

        #
        # Resolve the source root path.
        #
        if os.path.isdir(project_path):
            source_root_path = self.source_root_path
            if source_root_path is not None:
                original_source_root_path = source_root_path
                if not os.path.isabs(source_root_path):
                    source_root_path = os.path.join(
                        project_path, source_root_path
                    )
                    source_root_path = os.path.abspath(source_root_path)
                if not os.path.isdir(source_root_path):
                    raise ValueError(
                        "config: "
                        "source_root_path: "
                        f"Provided path does not exist: "
                        f"{original_source_root_path}."
                    )
                self.source_root_path = source_root_path

        #
        # Read exclude paths from .gitignore. Add them to the user project's
        # both SDoc and source file search paths.
        #
        path_to_gitignore = os.path.join(project_path, ".gitignore")
        if os.path.isfile(path_to_gitignore):
            patterns = ["/.git/"]

            with open(path_to_gitignore, encoding="utf-8") as f:
                for line_ in f:
                    line = line_.strip()
                    if not line or line.startswith("#"):
                        continue
                    # Ignore !-negated gitignores for now or reimplement
                    # using a dedicated gitignore Python library.
                    if line.startswith("!"):
                        continue
                    patterns.append(line)

            self.exclude_doc_paths.extend(patterns)
            self.exclude_source_paths.extend(patterns)

        #
        # Validate that the provided grammar shortcuts all point to existing
        # grammar files.
        #
        for grammar_alias_, grammar_path_ in list(self.grammars.items()):
            assert grammar_alias_.startswith("@"), (
                "Grammar alias must start with an '@' character."
            )
            assert "." not in grammar_alias_, (
                "Grammar alias must not contain any . characters."
            )
            assert os.path.isfile(os.path.join(project_path, grammar_path_)), (
                "Grammar path must point to an existing path relative to the "
                f"project config file: {grammar_path_}."
            )
            if grammar_path_.startswith("./"):
                self.grammars[grammar_alias_] = grammar_path_.removeprefix("./")

    def is_feature_activated(self, feature: ProjectFeature) -> bool:
        return feature in self.project_features

    def is_activated_table_screen(self) -> bool:
        return ProjectFeature.TABLE_SCREEN in self.project_features

    def is_activated_trace_screen(self) -> bool:
        return ProjectFeature.TRACEABILITY_SCREEN in self.project_features

    def is_activated_deep_trace_screen(self) -> bool:
        return ProjectFeature.DEEP_TRACEABILITY_SCREEN in self.project_features

    def is_activated_project_statistics(self) -> bool:
        return ProjectFeature.PROJECT_STATISTICS_SCREEN in self.project_features

    def is_activated_requirements_to_source_traceability(self) -> bool:
        return (
            ProjectFeature.REQUIREMENT_TO_SOURCE_TRACEABILITY
            in self.project_features
        )

    def is_activated_requirements_coverage(self) -> bool:
        return (
            ProjectFeature.TRACEABILITY_MATRIX_SCREEN in self.project_features
        )

    def is_activated_tree_map(self) -> bool:
        return ProjectFeature.TREE_MAP_SCREEN in self.project_features

    def is_activated_standalone_document(self) -> bool:
        return (
            ProjectFeature.STANDALONE_DOCUMENT_SCREEN in self.project_features
        )

    def is_activated_search(self) -> bool:
        return (
            self.is_running_on_server
            and ProjectFeature.SEARCH in self.project_features
        )

    def is_activated_html2pdf(self) -> bool:
        return ProjectFeature.HTML2PDF in self.project_features

    def is_activated_diff(self) -> bool:
        return ProjectFeature.DIFF in self.project_features

    def is_activated_reqif(self) -> bool:
        return ProjectFeature.REQIF in self.project_features

    def is_activated_mathjax(self) -> bool:
        return ProjectFeature.MATHJAX in self.project_features

    def is_activated_mermaid(self) -> bool:
        return ProjectFeature.MERMAID in self.project_features

    def is_activated_rapidoc(self) -> bool:
        return ProjectFeature.RAPIDOC in self.project_features

    def is_activated_source_file_language_parsers(self) -> bool:
        return (
            ProjectFeature.SOURCE_FILE_LANGUAGE_PARSERS in self.project_features
        )

    def get_project_root_path(self) -> str:
        if self.input_paths is not None and len(self.input_paths) > 0:
            return self.input_paths[0]
        raise NotImplementedError

    def get_strictdoc_root_path(self) -> str:
        return self.environment.path_to_strictdoc

    def get_path_to_cache_dir(self) -> str:
        return self.dir_for_sdoc_cache

    def get_static_files_path(self) -> str:
        return self.environment.get_static_files_path()

    def get_extra_static_files_path(self) -> str:
        return self.environment.get_extra_static_files_path()

    def get_project_hash(self) -> str:
        assert self.input_paths is not None and len(self.input_paths) > 0
        return get_md5(self.input_paths[0])

    def get_relevant_source_nodes_entry(
        self, path_to_file: str
    ) -> Optional[SourceNodesEntry]:
        """
        Get relevant source_nodes config item for a given source code file.

        Returns data for the first entry from source_nodes that is a parent path of path_to_file.
        If path_to_file is absolute, source node config entries are assumed to be in the source_root_path.
        """

        source_root_path = self.source_root_path
        assert source_root_path is not None
        assert os.path.exists(source_root_path), source_root_path

        source_file_path = Path(path_to_file)
        for sdoc_source_config_entry_ in self.source_nodes:
            # FIXME: Move the setting of full paths to .finalize() of this config
            #        class when it is implemented.
            if sdoc_source_config_entry_.full_path is None:
                sdoc_source_config_entry_.full_path = Path(
                    source_root_path
                ) / Path(sdoc_source_config_entry_.path)

            if source_file_path.is_absolute():
                if (
                    sdoc_source_config_entry_.full_path
                    in source_file_path.parents
                ):
                    return sdoc_source_config_entry_
            else:
                if (
                    Path(sdoc_source_config_entry_.path)
                    in source_file_path.parents
                ):
                    return sdoc_source_config_entry_

        return None


class ProjectConfigLoader:
    @classmethod
    def load(
        cls, input_path: str, output_dir: Optional[str] = None
    ) -> ProjectConfig:
        assert os.path.exists(input_path), input_path
        project_config: ProjectConfig = cls.load_from_path_or_get_default(
            path_to_config=input_path
        )
        project_config.input_paths = [input_path]
        if output_dir is not None:
            project_config.output_dir = output_dir
        project_config.validate_and_finalize()
        return project_config

    @classmethod
    def load_using_export_config(
        cls,
        export_config: ExportCommandConfig,
    ) -> ProjectConfig:
        path_to_config = export_config.get_path_to_config()
        project_config: ProjectConfig = cls.load_from_path_or_get_default(
            path_to_config=path_to_config
        )
        project_config.integrate_export_config(export_config)
        project_config.validate_and_finalize()
        return project_config

    @classmethod
    def load_using_server_config(
        cls,
        server_config: ServerCommandConfig,
    ) -> ProjectConfig:
        path_to_config = server_config.get_path_to_config()
        project_config: ProjectConfig = cls.load_from_path_or_get_default(
            path_to_config=path_to_config
        )
        project_config.integrate_server_config(server_config)
        project_config.validate_and_finalize()
        return project_config

    @classmethod
    def load_using_import_excel_config(
        cls,
        _: ImportExcelCommandConfig,
    ) -> ProjectConfig:
        path_to_config = os.getcwd()
        project_config: ProjectConfig = cls.load_from_path_or_get_default(
            path_to_config=path_to_config
        )
        project_config.input_paths = [path_to_config]
        project_config.validate_and_finalize()
        return project_config

    @classmethod
    def load_using_import_reqif_config(
        cls,
        _: ImportReqIFCommandConfig,
    ) -> ProjectConfig:
        path_to_config = os.getcwd()
        project_config: ProjectConfig = cls.load_from_path_or_get_default(
            path_to_config=path_to_config
        )
        project_config.input_paths = [path_to_config]
        project_config.validate_and_finalize()
        return project_config

    @classmethod
    def load_using_manage_autouid_config(
        cls,
        manage_autouid_config: ManageAutoUIDCommandConfig,
    ) -> ProjectConfig:
        path_to_config = manage_autouid_config.get_path_to_config()

        project_config: ProjectConfig = cls.load_from_path_or_get_default(
            path_to_config=path_to_config
        )

        # FIXME: Encapsulate all this in project_config.integrate_manage_autouid_config(),
        #        following the example of integrate_export_config().
        project_config.input_paths = [manage_autouid_config.input_path]
        project_config.source_root_path = str(
            Path(manage_autouid_config.input_path).resolve()
        )
        project_config.auto_uid_mode = True
        project_config.autouuid_include_sections = (
            manage_autouid_config.include_sections
        )

        # FIXME: Traceability Index is coupled with HTML output.
        project_config.export_output_html_root = "NOT_RELEVANT"

        project_config.validate_and_finalize()

        return project_config

    @staticmethod
    def load_from_path_or_get_default(
        *,
        path_to_config: str,
    ) -> ProjectConfig:
        if not os.path.exists(path_to_config):
            return ProjectConfig.default_config()
        if os.path.isdir(path_to_config):
            path_to_config_dir = path_to_config
            path_to_config = os.path.join(path_to_config_dir, "strictdoc.toml")
            if not os.path.isfile(path_to_config):
                path_to_config = os.path.join(
                    path_to_config_dir, "strictdoc_config.py"
                )

        if not os.path.isfile(path_to_config):
            return ProjectConfig.default_config()

        if path_to_config.endswith("strictdoc_config.py"):
            return ProjectConfigLoader.load_from_python(
                config_py_path=path_to_config
            )

        try:
            config_content = toml.load(path_to_config)
        except toml.decoder.TomlDecodeError as exception:
            raise StrictDocException(  # noqa: T201
                f"Could not parse the config file {path_to_config}: "
                f"{exception}."
            ) from None
        except Exception as exception:  # pragma: no cover
            raise AssertionError from exception

        DEPRECATION_ENGINE.add_message(
            "DEPRECATED_CONFIG_TOML",
            (
                "WARNING: StrictDoc TOML configuration format is deprecated. "
                "Replace the TOML config file with a Python config file.\n\n"
                "See the migration guide for mode details:\n\n"
                "https://strictdoc.readthedocs.io/en/stable/?a=SECTION-UG-MIGRATE-CONFIG-2025-Q4"
            ),
        )

        config_last_update = get_file_modification_time(path_to_config)

        return ProjectConfigLoader._load_from_dictionary(
            config_dict=config_content,
            config_last_update=config_last_update,
        )

    @staticmethod
    def load_from_python(*, config_py_path: str) -> ProjectConfig:
        module = import_from_path(config_py_path)
        create_config_function = module.create_config
        assert isinstance(create_config_function, types.FunctionType), type(
            create_config_function
        )
        project_config = create_config_function()
        assert isinstance(project_config, ProjectConfig)
        return project_config

    @staticmethod
    def _load_from_dictionary(
        *,
        config_dict: Dict[str, Any],
        config_last_update: Optional[datetime.datetime],
    ) -> ProjectConfig:
        project_title = ProjectConfigDefault.DEFAULT_PROJECT_TITLE
        dir_for_sdoc_assets = ProjectConfigDefault.DEFAULT_DIR_FOR_SDOC_ASSETS
        dir_for_sdoc_cache = ProjectConfigDefault.DEFAULT_DIR_FOR_SDOC_CACHE
        project_features = ProjectConfigDefault.DEFAULT_FEATURES
        server_host = ProjectConfigDefault.DEFAULT_SERVER_HOST
        server_port = ProjectConfigDefault.DEFAULT_SERVER_PORT
        include_doc_paths: List[str] = []
        exclude_doc_paths: List[str] = []
        source_root_path = None
        include_source_paths: List[str] = []
        exclude_source_paths: List[str] = []
        test_report_root_dict: Dict[str, str] = {}
        source_nodes: List[SourceNodesEntry] = []
        html2pdf_strict: bool = False
        html2pdf_template: Optional[str] = None
        bundle_document_version = (
            ProjectConfigDefault.DEFAULT_BUNDLE_DOCUMENT_VERSION
        )
        bundle_document_date = (
            ProjectConfigDefault.DEFAULT_BUNDLE_DOCUMENT_COMMIT_DATE
        )

        traceability_matrix_relation_columns: Optional[
            List[Tuple[str, Optional[str]]]
        ] = None
        reqif_profile = ReqIFProfile.P01_SDOC
        reqif_multiline_is_xhtml = False
        reqif_enable_mid = False
        reqif_import_markup: Optional[str] = None
        chromedriver: Optional[str] = None

        section_behavior: str = ProjectConfigDefault.DEFAULT_SECTION_BEHAVIOR
        statistics_generator: Optional[str] = None

        if "project" in config_dict:
            project_content = config_dict["project"]
            project_title = project_content.get("title", project_title)
            dir_for_sdoc_assets = project_content.get(
                "html_assets_strictdoc_dir", dir_for_sdoc_assets
            )
            dir_for_sdoc_cache = project_content.get(
                "cache_dir", dir_for_sdoc_cache
            )

            project_features = project_content.get("features", project_features)

            statistics_generator = project_content.get(
                "statistics_generator", statistics_generator
            )

            include_doc_paths = project_content.get(
                "include_doc_paths", include_doc_paths
            )

            exclude_doc_paths = project_content.get(
                "exclude_doc_paths", exclude_doc_paths
            )

            source_root_path = project_content.get(
                "source_root_path", source_root_path
            )

            include_source_paths = project_content.get(
                "include_source_paths", include_source_paths
            )

            exclude_source_paths = project_content.get(
                "exclude_source_paths", exclude_source_paths
            )

            html2pdf_strict = project_content.get(
                "html2pdf_strict", html2pdf_strict
            )

            html2pdf_template = project_content.get(
                "html2pdf_template", html2pdf_template
            )

            bundle_document_version = project_content.get(
                "bundle_document_version", bundle_document_version
            )

            bundle_document_date = project_content.get(
                "bundle_document_date", bundle_document_date
            )

            traceability_matrix_relation_columns_config: Optional[List[str]] = (
                project_content.get(
                    "traceability_matrix_relation_columns", None
                )
            )
            if traceability_matrix_relation_columns_config is not None:
                assert isinstance(
                    traceability_matrix_relation_columns_config, list
                )
                traceability_matrix_relation_columns = []
                for (
                    relation_column_string_
                ) in traceability_matrix_relation_columns_config:
                    relation_tuple = parse_relation_tuple(
                        relation_column_string_
                    )
                    assert relation_tuple is not None
                    traceability_matrix_relation_columns.append(relation_tuple)

            chromedriver = project_content.get("chromedriver", chromedriver)

            if (
                test_report_root_dict_ := project_content.get(
                    "test_report_root_dict", None
                )
            ) is not None:
                assert isinstance(test_report_root_dict_, list), (
                    test_report_root_dict
                )
                for test_report_root_entry_ in test_report_root_dict_:
                    assert isinstance(test_report_root_entry_, dict)
                    test_report_root_dict.update(test_report_root_entry_)

            section_behavior = project_content.get(
                "section_behavior", section_behavior
            )
            assert section_behavior in ("[SECTION]", "[[SECTION]]")

            if "source_nodes" in project_content:
                source_nodes_config = project_content["source_nodes"]
                assert isinstance(source_nodes_config, list)
                for item_ in source_nodes_config:
                    source_node_path = next(iter(item_))
                    source_node_item = item_[source_node_path]
                    source_nodes.append(
                        SourceNodesEntry(
                            path=source_node_path,
                            uid=source_node_item["uid"],
                            node_type=source_node_item["node_type"],
                            sdoc_to_source_map=source_node_item["map"]
                            if "map" in source_node_item
                            else {},
                        )
                    )

        if "server" in config_dict:
            server_content = config_dict["server"]
            server_host = server_content.get("host", server_host)
            server_port = server_content.get("port", server_port)

        if "reqif" in config_dict:
            reqif_content = config_dict["reqif"]
            reqif_multiline_is_xhtml = reqif_content.get(
                "multiline_is_xhtml", False
            )
            reqif_enable_mid = reqif_content.get("enable_mid", False)
            reqif_import_markup = reqif_content.get("import_markup", None)

        return ProjectConfig(
            project_title=project_title,
            dir_for_sdoc_assets=dir_for_sdoc_assets,
            dir_for_sdoc_cache=dir_for_sdoc_cache,
            project_features=project_features,
            server_host=server_host,
            server_port=server_port,
            include_doc_paths=include_doc_paths,
            exclude_doc_paths=exclude_doc_paths,
            source_root_path=source_root_path,
            include_source_paths=include_source_paths,
            exclude_source_paths=exclude_source_paths,
            test_report_root_dict=test_report_root_dict,
            source_nodes=source_nodes,
            html2pdf_strict=html2pdf_strict,
            html2pdf_template=html2pdf_template,
            bundle_document_version=bundle_document_version,
            bundle_document_date=bundle_document_date,
            traceability_matrix_relation_columns=traceability_matrix_relation_columns,
            reqif_profile=reqif_profile,
            reqif_multiline_is_xhtml=reqif_multiline_is_xhtml,
            reqif_enable_mid=reqif_enable_mid,
            reqif_import_markup=reqif_import_markup,
            chromedriver=chromedriver,
            section_behavior=section_behavior,
            statistics_generator=statistics_generator,
            _config_last_update=config_last_update,
        )
