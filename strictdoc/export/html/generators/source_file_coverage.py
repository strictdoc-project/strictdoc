# mypy: disable-error-code="no-untyped-call,no-untyped-def"
from typing import Optional

from strictdoc import __version__
from strictdoc.backend.sdoc_source_code.models.source_file_info import (
    SourceFileTraceabilityInfo,
)
from strictdoc.core.project_config import ProjectConfig
from strictdoc.core.source_tree import SourceFile
from strictdoc.core.traceability_index import TraceabilityIndex
from strictdoc.export.html.html_templates import HTMLTemplates, JinjaEnvironment
from strictdoc.export.html.renderers.link_renderer import LinkRenderer


class SourceCoverageViewObject:
    def __init__(
        self,
        *,
        traceability_index: TraceabilityIndex,
        project_config: ProjectConfig,
    ):
        self.traceability_index: TraceabilityIndex = traceability_index
        self.project_config: ProjectConfig = project_config
        self.link_renderer: LinkRenderer = LinkRenderer(
            root_path="", static_path=project_config.dir_for_sdoc_assets
        )
        self.standalone: bool = False
        self.is_running_on_server: bool = project_config.is_running_on_server
        self.strictdoc_version = __version__

    def render_screen(self, jinja_environment: JinjaEnvironment):
        return jinja_environment.render_template_as_markup(
            "screens/source_file_coverage/index.jinja", view_object=self
        )

    def render_static_url(self, url: str):
        return self.link_renderer.render_static_url(url)

    def render_url(self, url: str):
        return self.link_renderer.render_url(url)

    def render_static_url_with_prefix(self, url: str):
        return self.link_renderer.render_static_url_with_prefix(url)

    def render_local_anchor(self, node):
        return self.link_renderer.render_local_anchor(node)

    def get_file_stats_lines_total(self, source_file: SourceFile) -> str:
        trace_info: Optional[SourceFileTraceabilityInfo] = (
            self.traceability_index.get_coverage_info_weak(
                source_file.in_doctree_source_file_rel_path_posix
            )
        )
        if trace_info is None:
            return "0"
        return str(trace_info.file_stats.lines_total)

    def get_file_stats_lines_total_non_empty(
        self, source_file: SourceFile
    ) -> str:
        trace_info: Optional[SourceFileTraceabilityInfo] = (
            self.traceability_index.get_coverage_info_weak(
                source_file.in_doctree_source_file_rel_path_posix
            )
        )
        if trace_info is None:
            return "0"
        return str(trace_info.file_stats.lines_non_empty)

    def get_file_stats_non_empty_lines_covered(
        self, source_file: SourceFile
    ) -> str:
        trace_info: Optional[SourceFileTraceabilityInfo] = (
            self.traceability_index.get_coverage_info_weak(
                source_file.in_doctree_source_file_rel_path_posix
            )
        )
        if trace_info is None:
            return "0"
        return str(trace_info.ng_lines_covered)

    def get_file_stats_non_empty_lines_covered_percentage(
        self, source_file: SourceFile
    ) -> str:
        trace_info: Optional[SourceFileTraceabilityInfo] = (
            self.traceability_index.get_coverage_info_weak(
                source_file.in_doctree_source_file_rel_path_posix
            )
        )
        if trace_info is None:
            return f"{0:.1f}"
        covered = trace_info.ng_lines_covered
        total_non_empty = trace_info.file_stats.lines_non_empty
        percentage = (
            (covered / total_non_empty * 100) if total_non_empty > 0 else 0
        )
        return f"{percentage:.1f}"

    def get_file_stats_functions_total(self, source_file: SourceFile) -> str:
        trace_info: Optional[SourceFileTraceabilityInfo] = (
            self.traceability_index.get_coverage_info_weak(
                source_file.in_doctree_source_file_rel_path_posix
            )
        )
        if trace_info is None:
            return "0"
        return str(len(trace_info.functions))

    def get_file_stats_functions_covered(self, source_file: SourceFile) -> str:
        trace_info: Optional[SourceFileTraceabilityInfo] = (
            self.traceability_index.get_coverage_info_weak(
                source_file.in_doctree_source_file_rel_path_posix
            )
        )
        if trace_info is None:
            return "0"
        return str(trace_info.covered_functions)

    def get_file_stats_functions_covered_percentage(
        self, source_file: SourceFile
    ) -> str:
        trace_info: Optional[SourceFileTraceabilityInfo] = (
            self.traceability_index.get_coverage_info_weak(
                source_file.in_doctree_source_file_rel_path_posix
            )
        )
        if trace_info is None:
            return f"{0:.1f}"
        covered = trace_info.covered_functions
        total = len(trace_info.functions)
        percentage = (covered / total * 100) if total > 0 else 0
        return f"{percentage:.1f}"


class SourceFileCoverageHTMLGenerator:
    @staticmethod
    def export(
        *,
        project_config: ProjectConfig,
        traceability_index: TraceabilityIndex,
        html_templates: HTMLTemplates,
    ):
        view_object = SourceCoverageViewObject(
            traceability_index=traceability_index,
            project_config=project_config,
        )
        return view_object.render_screen(html_templates.jinja_environment())
