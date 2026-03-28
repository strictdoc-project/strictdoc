from dataclasses import dataclass
from math import ceil, floor
from typing import List, Optional

from markupsafe import Markup

from strictdoc import __version__
from strictdoc.backend.sdoc.models.document import SDocDocument
from strictdoc.backend.sdoc.models.node import SDocNode
from strictdoc.core.project_config import ProjectConfig
from strictdoc.core.traceability_index import TraceabilityIndex
from strictdoc.export.html.document_type import DocumentType
from strictdoc.export.html.html_templates import JinjaEnvironment
from strictdoc.export.html.renderers.link_renderer import LinkRenderer


@dataclass
class WorkPlannerDocumentOption:
    mid: str
    title: str


@dataclass
class WorkPlannerMonth:
    index: int
    label: str


@dataclass
class WorkPlannerEpicCard:
    node: SDocNode
    document: SDocDocument
    title: str
    statement: str
    status: str
    status_css_class: str
    time_start: Optional[str]
    time_end: Optional[str]
    work_package_uid: Optional[str]
    start_month_index: int
    end_month_index: int
    start_offset: float = 0.0
    end_offset: float = 1.0
    stack_level: int = 0

    @property
    def month_span(self) -> int:
        return self.end_month_index - self.start_month_index + 1

    @property
    def grid_column_start(self) -> int:
        return int(floor(self.start_offset)) + 1

    @property
    def grid_column_end(self) -> int:
        return int(ceil(self.end_offset)) + 1

    @property
    def start_inset(self) -> float:
        return self.start_offset - floor(self.start_offset)

    @property
    def end_inset(self) -> float:
        return ceil(self.end_offset) - self.end_offset


@dataclass
class WorkPlannerLane:
    title: str
    subtitle: Optional[str]
    epics: List[WorkPlannerEpicCard]

    @property
    def row_count(self) -> int:
        if len(self.epics) == 0:
            return 1
        return max(epic.stack_level for epic in self.epics) + 1


@dataclass
class WorkPlannerBacklogWorkPackage:
    node: SDocNode
    document: SDocDocument
    title: str
    statement: str
    epics: List[WorkPlannerEpicCard]


class WorkPlannerViewObject:
    def __init__(
        self,
        *,
        traceability_index: TraceabilityIndex,
        project_config: ProjectConfig,
        link_renderer: LinkRenderer,
        documents: List[WorkPlannerDocumentOption],
        default_document_mid: Optional[str],
        months: List[WorkPlannerMonth],
        all_epics_lane: WorkPlannerLane,
        backlog_work_packages: List[WorkPlannerBacklogWorkPackage],
        backlog_epics: List[WorkPlannerEpicCard],
    ) -> None:
        self.traceability_index: TraceabilityIndex = traceability_index
        self.project_config: ProjectConfig = project_config
        self.link_renderer: LinkRenderer = link_renderer
        self.documents: List[WorkPlannerDocumentOption] = documents
        self.default_document_mid: Optional[str] = default_document_mid
        self.months: List[WorkPlannerMonth] = months
        self.all_epics_lane: WorkPlannerLane = all_epics_lane
        self.backlog_work_packages: List[WorkPlannerBacklogWorkPackage] = (
            backlog_work_packages
        )
        self.backlog_epics: List[WorkPlannerEpicCard] = backlog_epics
        self.standalone: bool = False
        self.is_running_on_server: bool = project_config.is_running_on_server
        self.strictdoc_version = __version__

    def get_document_level(self) -> int:
        return 0

    def render_screen(self, jinja_environment: JinjaEnvironment) -> Markup:
        return jinja_environment.render_template_as_markup(
            "screens/work_planner/index.jinja", view_object=self
        )

    def render_frame_content(
        self, jinja_environment: JinjaEnvironment
    ) -> Markup:
        return jinja_environment.render_template_as_markup(
            "screens/work_planner/frame_content.jinja.html",
            view_object=self,
        )

    def render_static_url(self, url: str) -> str:
        return self.link_renderer.render_static_url(url)

    def render_static_url_with_prefix(self, url: str) -> str:
        return self.link_renderer.render_static_url_with_prefix(url)

    def render_url(self, url: str) -> str:
        return self.link_renderer.render_url(url)

    def render_node_link(self, node: SDocNode) -> str:
        return self.link_renderer.render_node_link(
            node, None, DocumentType.DOCUMENT
        )
