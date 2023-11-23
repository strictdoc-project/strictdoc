import os
import subprocess
from copy import deepcopy
from datetime import datetime
from typing import Optional

from fastapi import APIRouter
from starlette.responses import HTMLResponse, Response

from strictdoc import __version__
from strictdoc.core.document_tree_iterator import DocumentTreeIterator
from strictdoc.core.project_config import ProjectConfig
from strictdoc.core.traceability_index import TraceabilityIndex
from strictdoc.core.traceability_index_builder import TraceabilityIndexBuilder
from strictdoc.export.html.document_type import DocumentType
from strictdoc.export.html.html_templates import HTMLTemplates
from strictdoc.export.html.renderers.link_renderer import LinkRenderer
from strictdoc.git.git_client import GitClient
from strictdoc.git.project_diff_analyzer import (
    ProjectDiffAnalyzer,
    ProjectTreeDiffStats,
)
from strictdoc.helpers.parallelizer import NullParallelizer
from strictdoc.helpers.timing import measure_performance
from strictdoc.server.routers.main_router import HTTP_STATUS_PRECONDITION_FAILED


def create_other_router(project_config: ProjectConfig) -> APIRouter:
    router = APIRouter()

    html_templates = HTMLTemplates.create(
        project_config=project_config,
        enable_caching=False,
        strictdoc_last_update=datetime.today(),
    )

    @router.get("/diff")
    def get_git_diff(
        left_revision: Optional[str] = None,
        right_revision: Optional[str] = None,
    ):
        if not project_config.is_activated_diff():
            return Response(
                content="The DIFF feature is not activated in the project config.",
                status_code=HTTP_STATUS_PRECONDITION_FAILED,
            )
        left_revision_resolved = None
        right_revision_resolved = None
        results = False

        if left_revision is not None:
            assert right_revision is not None

            git_client = GitClient(".")
            try:
                if left_revision != "HEAD+":
                    left_revision_resolved = git_client.check_revision(
                        left_revision
                    )
                else:
                    return HTMLResponse(
                        content=(
                            "Left revision argument 'HEAD+' is not supported. "
                            "'HEAD+' can only be used as a right revision argument."
                        ),
                        status_code=412,
                    )

                if right_revision != "HEAD+":
                    right_revision_resolved = git_client.check_revision(
                        right_revision
                    )
                else:
                    right_revision_resolved = "HEAD+"
            except LookupError as exception_:
                return HTMLResponse(content=exception_.args[0], status_code=404)
            results = True

        template = html_templates.jinja_environment().get_template(
            "screens/git/index.jinja"
        )

        link_renderer = LinkRenderer(
            root_path="", static_path=project_config.dir_for_sdoc_assets
        )
        if not results:
            output = template.render(
                project_config=project_config,
                document_type=DocumentType.document(),
                link_document_type=DocumentType.document(),
                standalone=False,
                strictdoc_version=__version__,
                link_renderer=link_renderer,
                results=False,
                left_revision=None,
                right_revision=None,
            )
            return HTMLResponse(content=output, status_code=200)

        assert left_revision_resolved is not None
        assert right_revision_resolved is not None

        path_to_cwd = os.getcwd()
        path_to_sandbox_dir = "/tmp/sandbox"

        with measure_performance("RSYNC"):
            result = subprocess.run(
                [
                    "rsync",
                    # "-vvraP",
                    "-r",
                    "--partial",
                    "--delete",
                    "--exclude=build/",
                    "--exclude=__pycache__/",
                    "--exclude=.ruff_cache/",
                    "--exclude=output/",
                    "--exclude=strictdoc-project.github.io/",
                    ".",
                    path_to_sandbox_dir,
                ],
                cwd=path_to_cwd,
                capture_output=False,
                text=True,
                check=True,
            )
            assert result.returncode == 0, result

        git_client = GitClient(path_to_sandbox_dir)
        if right_revision_resolved != "HEAD+":
            git_client.hard_reset(revision=right_revision_resolved)
            git_client.clean()

        parallelizer = NullParallelizer()

        project_config_copy: ProjectConfig = deepcopy(project_config)
        assert project_config_copy.export_input_paths is not None
        export_input_rel_path = os.path.relpath(
            project_config_copy.export_input_paths[0], os.getcwd()
        )
        export_input_abs_path = os.path.join(
            path_to_sandbox_dir, export_input_rel_path
        )
        project_config_copy.export_input_paths = [export_input_abs_path]

        traceability_index_rhs: TraceabilityIndex = (
            TraceabilityIndexBuilder.create(
                project_config=project_config_copy,
                parallelizer=parallelizer,
            )
        )

        if left_revision_resolved != "HEAD+":
            git_client.hard_reset(revision=left_revision_resolved)
            git_client.clean()

        traceability_index_lhs: TraceabilityIndex = (
            TraceabilityIndexBuilder.create(
                project_config=project_config_copy,
                parallelizer=parallelizer,
            )
        )

        lhs_stats: ProjectTreeDiffStats = (
            ProjectDiffAnalyzer.analyze_document_tree(traceability_index_lhs)
        )
        rhs_stats: ProjectTreeDiffStats = (
            ProjectDiffAnalyzer.analyze_document_tree(traceability_index_rhs)
        )

        documents_iterator_lhs = DocumentTreeIterator(
            traceability_index_lhs.document_tree
        )
        documents_iterator_rhs = DocumentTreeIterator(
            traceability_index_rhs.document_tree
        )
        output = template.render(
            project_config=project_config,
            document_tree_lhs=traceability_index_lhs.document_tree,
            document_tree_rhs=traceability_index_rhs.document_tree,
            documents_iterator_lhs=documents_iterator_lhs,
            documents_iterator_rhs=documents_iterator_rhs,
            left_revision=left_revision,
            right_revision=right_revision,
            lhs_stats=lhs_stats,
            rhs_stats=rhs_stats,
            traceability_index_lhs=traceability_index_lhs,
            traceability_index_rhs=traceability_index_rhs,
            link_renderer=link_renderer,
            document_type=DocumentType.document(),
            link_document_type=DocumentType.document(),
            standalone=False,
            strictdoc_version=__version__,
            results=True,
        )
        return HTMLResponse(
            content=output,
            status_code=200,
        )

    return router
