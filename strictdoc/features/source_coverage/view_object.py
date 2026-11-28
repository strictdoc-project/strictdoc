from dataclasses import dataclass
from typing import List, Optional, Union

from markupsafe import Markup

from strictdoc import __version__
from strictdoc.backend.sdoc_source_code.models.source_file_info import (
    SourceFileTraceabilityInfo,
)
from strictdoc.core.file_system.file_tree import File, Folder
from strictdoc.core.file_system.source_tree import SourceFile, SourceTree
from strictdoc.core.project_config import ProjectConfig
from strictdoc.core.traceability_index import (
    TraceabilityIndex,
)
from strictdoc.export.html.html_templates import JinjaEnvironment
from strictdoc.export.html.renderers.link_renderer import LinkRenderer
from strictdoc.helpers.cast import assert_cast


class SourceCoverageViewObject:
    def __init__(
        self,
        *,
        traceability_index: TraceabilityIndex,
        project_config: ProjectConfig,
    ) -> None:
        self.traceability_index: TraceabilityIndex = traceability_index
        self.project_config: ProjectConfig = project_config
        self.link_renderer: LinkRenderer = LinkRenderer(
            root_path="", static_path=project_config.dir_for_sdoc_assets
        )
        self.is_running_on_server: bool = project_config.is_running_on_server
        self.strictdoc_version = __version__

    def get_document_level(self) -> int:
        return 0

    def render_screen(self, jinja_environment: JinjaEnvironment) -> Markup:
        return jinja_environment.render_template_as_markup(
            "features/source_coverage/index.jinja", view_object=self
        )

    def render_static_url(self, url: str) -> str:
        return self.link_renderer.render_static_url(url)

    def render_url(self, url: str) -> str:
        # FIXME: Switch to Markup(...).
        return self.link_renderer.render_url(url)

    def get_rows(
        self,
    ) -> List[Union["SourceCoverageFolderRow", "SourceCoverageFileRow"]]:
        """
        Return the rows of the coverage table, in the order of the table: a
        folder row, then the rows of its subfolders, then the rows of its
        files.

        The template loops over these rows. A row has all its values already,
        so the template needs no include and no helper call per row. The
        source tree of the StrictDoc repository gives about 3,000 rows.
        """
        source_tree = assert_cast(
            self.traceability_index.document_tree.source_tree, SourceTree
        )
        rows: List[Union[SourceCoverageFolderRow, SourceCoverageFileRow]] = []
        root_folder_or_file = source_tree.file_tree.root_folder_or_file
        if isinstance(root_folder_or_file, Folder):
            if root_folder_or_file.has_content():
                self._add_folder_rows(source_tree, root_folder_or_file, rows)
        else:
            rows.append(
                self._create_file_row(
                    source_tree, root_folder_or_file, indent=""
                )
            )
        return rows

    def _add_folder_rows(
        self,
        source_tree: SourceTree,
        folder: Folder,
        rows: List[Union["SourceCoverageFolderRow", "SourceCoverageFileRow"]],
    ) -> None:
        rows.append(
            SourceCoverageFolderRow(
                level=folder.level, folder_name=folder.folder_name
            )
        )
        for subfolder_ in folder.subfolder_trees:
            # has_sdoc_content is the result of has_content(), which
            # FileFinder already computed for the whole tree.
            if subfolder_.has_sdoc_content:
                self._add_folder_rows(source_tree, subfolder_, rows)
        for file_ in folder.files:
            rows.append(
                self._create_file_row(
                    source_tree, file_, indent=str(folder.level)
                )
            )

    def _create_file_row(
        self, source_tree: SourceTree, file: File, indent: str
    ) -> "SourceCoverageFileRow":
        source_file: SourceFile = source_tree.get_source_for_file(file)
        path = source_file.in_doctree_source_file_rel_path_posix
        link: Optional[str] = (
            self.link_renderer.render_source_file_link_from_root_2(source_file)
            if source_file.is_referenced
            else None
        )
        trace_info: Optional[SourceFileTraceabilityInfo] = (
            self.traceability_index.get_coverage_info_weak(path)
        )
        if trace_info is None:
            return SourceCoverageFileRow(
                indent=indent,
                file_name=file.file_name,
                path=path,
                link=link,
                lines_all="0",
                lines_total="0",
                lines_covered="0",
                lines_percent=f"{0:.1f}",
                func_total="0",
                func_covered="0",
                func_percent=f"{0:.1f}",
            )
        lines_non_empty = trace_info.file_stats.lines_non_empty
        lines_covered = trace_info.ng_lines_covered
        func_total = len(trace_info.functions)
        func_covered = trace_info.covered_functions
        lines_percent = (
            (lines_covered / lines_non_empty * 100)
            if lines_non_empty > 0
            else 0
        )
        func_percent = (
            (func_covered / func_total * 100) if func_total > 0 else 0
        )
        return SourceCoverageFileRow(
            indent=indent,
            file_name=file.file_name,
            path=path,
            link=link,
            lines_all=str(trace_info.file_stats.lines_total),
            lines_total=str(lines_non_empty),
            lines_covered=str(lines_covered),
            lines_percent=f"{lines_percent:.1f}",
            func_total=str(func_total),
            func_covered=str(func_covered),
            func_percent=f"{func_percent:.1f}",
        )


@dataclass(frozen=True)
class SourceCoverageFolderRow:
    level: int
    folder_name: str
    is_folder: bool = True


@dataclass(frozen=True)
class SourceCoverageFileRow:
    """
    The values of a file row, as the strings that the table shows.
    """

    # The level of the folder of the file, or "" for a single source file.
    indent: str
    file_name: str
    # The POSIX path of the file, relative to the source root.
    path: str
    # The link to the page of the file, or None if no node references it.
    link: Optional[str]
    lines_all: str
    lines_total: str
    lines_covered: str
    lines_percent: str
    func_total: str
    func_covered: str
    func_percent: str
    is_folder: bool = False
