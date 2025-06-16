# mypy: disable-error-code="arg-type,no-untyped-call,no-untyped-def"
import os
import urllib
from copy import deepcopy
from datetime import datetime
from typing import Optional

from fastapi import APIRouter
from starlette.responses import HTMLResponse, Response

from strictdoc import __version__
from strictdoc.core.project_config import ProjectConfig
from strictdoc.export.html.document_type import DocumentType
from strictdoc.export.html.generators.view_objects.diff_screen_results_view_object import (
    DiffScreenResultsViewObject,
)
from strictdoc.export.html.generators.view_objects.diff_screen_view_object import (
    DiffScreenViewObject,
)
from strictdoc.export.html.html_templates import HTMLTemplates
from strictdoc.export.html.renderers.link_renderer import LinkRenderer
from strictdoc.git.change_generator import ChangeContainer, ChangeGenerator
from strictdoc.git.git_client import GitClient
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
        tab: Optional[str] = None,
    ):
        if not project_config.is_activated_diff():
            return Response(
                content="The DIFF feature is not activated in the project config.",
                status_code=HTTP_STATUS_PRECONDITION_FAILED,
            )
        if tab is not None:
            if tab not in ("diff", "changelog"):
                return Response(
                    content="The tab= parameter must be either 'diff' or 'changelog'.",
                    status_code=HTTP_STATUS_PRECONDITION_FAILED,
                )
        else:
            tab = "diff"

        error_message: Optional[str] = None

        if (
            left_revision is not None
            and len(left_revision) > 0
            and right_revision is not None
            and len(right_revision) > 0
        ):
            git_client = GitClient(".")
            try:
                if left_revision != "HEAD+":
                    git_client.check_revision(left_revision)
                else:
                    raise LookupError(
                        "Left revision argument 'HEAD+' is not supported. "
                        "'HEAD+' can only be used as a right revision argument."
                    )

                if right_revision != "HEAD+":
                    git_client.check_revision(right_revision)
            except LookupError as exception_:
                error_message = exception_.args[0]
        elif (left_revision is not None and len(left_revision) > 0) or (
            right_revision is not None and len(right_revision) > 0
        ):
            error_message = "Valid Git revisions must be provided."
        else:
            # In the case when both revisions are empty, we load the starting
            # diff page.
            pass

        left_revision_urlencoded = (
            urllib.parse.quote(left_revision)
            if left_revision is not None
            else ""
        )
        right_revision_urlencoded = (
            urllib.parse.quote(right_revision)
            if right_revision is not None
            else ""
        )

        view_object = DiffScreenViewObject(
            project_config=project_config,
            results=False,
            left_revision=left_revision,
            left_revision_urlencoded=left_revision_urlencoded,
            right_revision=right_revision,
            right_revision_urlencoded=right_revision_urlencoded,
            error_message=error_message,
            tab=tab,
        )
        output = view_object.render_screen(html_templates.jinja_environment())
        status_code = 200 if error_message is None else 422
        return HTMLResponse(content=output, status_code=status_code)

    @router.get("/diff_result")
    def get_git_diff_result(
        left_revision: Optional[str] = None,
        right_revision: Optional[str] = None,
        tab: Optional[str] = None,
    ):
        if not project_config.is_activated_diff():
            return Response(
                content="The DIFF feature is not activated in the project config.",
                status_code=HTTP_STATUS_PRECONDITION_FAILED,
            )
        if tab is not None and tab not in ("diff", "changelog"):
            return Response(
                content="The tab= parameter must be either 'diff' or 'changelog'.",
                status_code=HTTP_STATUS_PRECONDITION_FAILED,
            )
        elif tab is None:
            tab = "diff"

        left_revision_resolved = None
        right_revision_resolved = None

        results = False
        error_message: Optional[str] = None

        if (
            left_revision is not None
            and len(left_revision) > 0
            and right_revision is not None
            and len(right_revision) > 0
        ):
            git_client = GitClient(".")
            try:
                if left_revision != "HEAD+":
                    left_revision_resolved = git_client.check_revision(
                        left_revision
                    )
                else:
                    raise LookupError(
                        "Left revision argument 'HEAD+' is not supported. "
                        "'HEAD+' can only be used as a right revision argument."
                    )

                if right_revision == "HEAD+":
                    right_revision_resolved = "HEAD+"
                else:
                    right_revision_resolved = git_client.check_revision(
                        right_revision
                    )

                results = True
            except LookupError as exception_:
                error_message = exception_.args[0]
        elif (left_revision is not None and len(left_revision) > 0) or (
            right_revision is not None and len(right_revision) > 0
        ):
            error_message = "Valid Git revisions must be provided."
        else:
            # In the case when both revisions are empty, we load the starting
            # diff page.
            pass

        path_to_template = (
            "screens/git/frame_changelog_result.jinja"
            if tab == "changelog"
            else "screens/git/frame_diff_result.jinja"
        )
        template = html_templates.jinja_environment().get_template(
            path_to_template
        )

        link_renderer = LinkRenderer(
            root_path="", static_path=project_config.dir_for_sdoc_assets
        )

        if not results:
            output = template.render(
                project_config=project_config,
                document_type=DocumentType.DOCUMENT.value,
                link_document_type=DocumentType.DOCUMENT.value,
                standalone=False,
                strictdoc_version=__version__,
                link_renderer=link_renderer,
                results=False,
                left_revision=left_revision,
                left_revision_urlencoded=urllib.parse.quote(left_revision),
                right_revision=right_revision,
                right_revision_urlencoded=urllib.parse.quote(right_revision),
                error_message=error_message,
            )
            status_code = 200 if error_message is None else 422
            return HTMLResponse(content=output, status_code=status_code)

        assert left_revision_resolved is not None
        assert right_revision_resolved is not None

        git_client_lhs = GitClient.create_repo_from_local_copy(
            left_revision_resolved, project_config
        )

        project_config_copy_lhs: ProjectConfig = deepcopy(project_config)
        assert project_config_copy_lhs.input_paths is not None
        project_config_copy_rhs: ProjectConfig = deepcopy(project_config)
        assert project_config_copy_rhs.input_paths is not None

        export_input_rel_path = os.path.relpath(
            project_config_copy_lhs.input_paths[0], os.getcwd()
        )
        export_input_abs_path = os.path.join(
            git_client_lhs.path_to_git_root, export_input_rel_path
        )
        project_config_copy_lhs.input_paths = [export_input_abs_path]

        git_client_rhs = GitClient.create_repo_from_local_copy(
            right_revision_resolved, project_config
        )

        export_input_rel_path = os.path.relpath(
            project_config_copy_rhs.input_paths[0], os.getcwd()
        )
        export_input_abs_path = os.path.join(
            git_client_rhs.path_to_git_root, export_input_rel_path
        )
        project_config_copy_rhs.input_paths = [export_input_abs_path]

        change_container: ChangeContainer = ChangeGenerator.generate(
            lhs_project_config=project_config_copy_lhs,
            rhs_project_config=project_config_copy_rhs,
        )

        view_object = DiffScreenResultsViewObject(
            project_config=project_config,
            change_container=change_container,
            document_tree_lhs=change_container.traceability_index_lhs.document_tree,
            document_tree_rhs=change_container.traceability_index_rhs.document_tree,
            documents_iterator_lhs=change_container.documents_iterator_lhs,
            documents_iterator_rhs=change_container.documents_iterator_rhs,
            left_revision=left_revision,
            left_revision_urlencoded=urllib.parse.quote(left_revision),
            right_revision=right_revision,
            right_revision_urlencoded=urllib.parse.quote(right_revision),
            lhs_stats=change_container.lhs_stats,
            rhs_stats=change_container.rhs_stats,
            change_stats=change_container.change_stats,
            traceability_index_lhs=change_container.traceability_index_lhs,
            traceability_index_rhs=change_container.traceability_index_rhs,
            tab=tab,
        )
        output = template.render(view_object=view_object)

        return HTMLResponse(
            content=output,
            status_code=200,
        )

    return router
