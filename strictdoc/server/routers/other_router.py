"""
@relation(SDOC-SRS-111, scope=file)
"""

import os
import urllib
from contextlib import ExitStack
from copy import deepcopy
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Form
from starlette.responses import HTMLResponse, RedirectResponse, Response

from strictdoc import __version__
from strictdoc.core.project_config import ProjectConfig
from strictdoc.export.html.document_type import DocumentType
from strictdoc.export.html.html_templates import HTMLTemplates
from strictdoc.export.html.renderers.link_renderer import LinkRenderer
from strictdoc.features.diff_and_changelog.change_container import (
    ChangeContainer,
)
from strictdoc.features.diff_and_changelog.change_generator import (
    ChangeGenerator,
)
from strictdoc.features.diff_and_changelog.diff_screen_results_view_object import (
    DiffScreenResultsViewObject,
)
from strictdoc.features.diff_and_changelog.diff_screen_view_object import (
    DiffScreenViewObject,
)
from strictdoc.features.diff_and_changelog.git_client import GitClient
from strictdoc.features.git_workspace.git_conflicts_view_object import (
    GitConflictsViewObject,
)
from strictdoc.features.git_workspace.git_status_service import (
    GitWorkspaceStatusService,
)
from strictdoc.features.git_workspace.git_workspace_view_object import (
    GitWorkspaceViewObject,
)
from strictdoc.features.git_workspace.sync_worktree_service import (
    SyncMergeService,
)
from strictdoc.features.git_workspace.three_way_merge_analyzer import (
    PLACEMENT_START,
    compute_parent_key_map,
)
from strictdoc.server.helpers.hierarchical_rw_lock_manager import (
    HierarchicalRWLockManager,
)
from strictdoc.server.routers.main_router import (
    HTTP_STATUS_BAD_REQUEST,
    HTTP_STATUS_PRECONDITION_FAILED,
)


def create_other_router(
    project_config: ProjectConfig,
    *,
    lock_manager: HierarchicalRWLockManager,
) -> APIRouter:
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
    ) -> Response:
        if not project_config.is_activated_diff():
            return Response(
                content="The DIFF feature is not activated in the project config.",
                status_code=HTTP_STATUS_PRECONDITION_FAILED,
            )
        if tab is not None:
            if tab not in ("diff", "changelog"):
                return Response(
                    content="The tab= parameter must be either 'diff' or 'changelog'.",
                    status_code=HTTP_STATUS_BAD_REQUEST,
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

        view_object = DiffScreenViewObject(
            project_config=project_config,
            results=False,
            left_revision=left_revision,
            right_revision=right_revision,
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
    ) -> Response:
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
            "features/diff_and_changelog/frame_changelog_result.jinja"
            if tab == "changelog"
            else "features/diff_and_changelog/frame_diff_result.jinja"
        )
        template = html_templates.jinja_environment().get_template(
            path_to_template
        )

        link_renderer = LinkRenderer(
            root_path="", static_path=project_config.dir_for_sdoc_assets
        )

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

        if not results:
            output = template.render(
                project_config=project_config,
                document_type=DocumentType.DOCUMENT.value,
                link_document_type=DocumentType.DOCUMENT.value,
                strictdoc_version=__version__,
                link_renderer=link_renderer,
                results=False,
                left_revision=left_revision,
                left_revision_urlencoded=left_revision_urlencoded,
                right_revision=right_revision,
                right_revision_urlencoded=right_revision_urlencoded,
                error_message=error_message,
            )
            status_code = 200 if error_message is None else 422
            return HTMLResponse(content=output, status_code=status_code)

        assert left_revision_resolved is not None
        assert right_revision_resolved is not None

        left_revision_tags = git_client.get_tags_for_revision(
            left_revision_resolved
        )
        right_revision_tags = (
            git_client.get_tags_for_revision(right_revision_resolved)
            if right_revision_resolved != "HEAD+"
            else []
        )

        def open_git_client_for_revision(revision: str) -> GitClient:
            if revision == "HEAD+":
                # Serialize HEAD+ snapshot creation with main router writes.
                with lock_manager.acquire_global_write():
                    return exit_stack.enter_context(
                        GitClient.create_cached_repo_from_local_copy(
                            revision, project_config
                        )
                    )
            return exit_stack.enter_context(
                GitClient.create_cached_repo_from_local_copy(
                    revision, project_config
                )
            )

        with ExitStack() as exit_stack:
            git_client_lhs = open_git_client_for_revision(
                left_revision_resolved
            )
            git_client_rhs = open_git_client_for_revision(
                right_revision_resolved
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

            assert (
                change_container.traceability_index_lhs.document_tree
                is not None
            )
            assert (
                change_container.traceability_index_rhs.document_tree
                is not None
            )
            # Unlike change_generator.py's static export, left_revision/
            # right_revision here must stay the raw expressions the user
            # submitted (e.g. "HEAD^"): the form/turbo-frame/nav-tab links
            # resubmit these exact values back to this route, so replacing
            # them with a "<expression> (<short-hash>)" display string would
            # break re-diffing from the results screen.
            view_object = DiffScreenResultsViewObject(
                project_config=project_config,
                change_container=change_container,
                document_tree_lhs=change_container.traceability_index_lhs.document_tree,
                document_tree_rhs=change_container.traceability_index_rhs.document_tree,
                documents_iterator_lhs=change_container.documents_iterator_lhs,
                documents_iterator_rhs=change_container.documents_iterator_rhs,
                left_revision=left_revision,
                right_revision=right_revision,
                left_revision_tags=left_revision_tags,
                right_revision_tags=right_revision_tags,
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

    def _redirect_to_git_workspace(
        target_branch: str,
        *,
        message: Optional[str] = None,
        error: Optional[str] = None,
    ) -> Response:
        params = {"target_branch": target_branch}
        if message is not None:
            params["message"] = message
        if error is not None:
            params["error"] = error
        query_string = urllib.parse.urlencode(params)
        return RedirectResponse(
            url=f"/git_workspace?{query_string}", status_code=303
        )

    def _redirect_to_git_conflicts(
        target_branch: str,
        *,
        message: Optional[str] = None,
        error: Optional[str] = None,
    ) -> Response:
        params = {"target_branch": target_branch}
        if message is not None:
            params["message"] = message
        if error is not None:
            params["error"] = error
        query_string = urllib.parse.urlencode(params)
        return RedirectResponse(
            url=f"/git_conflicts?{query_string}", status_code=303
        )

    def _default_target_branch(branches: List[str]) -> str:
        for candidate in ("main", "master"):
            if candidate in branches:
                return candidate
        return branches[0] if len(branches) > 0 else "main"

    @router.get("/git_workspace")
    def get_git_workspace(
        target_branch: Optional[str] = None,
        message: Optional[str] = None,
        error: Optional[str] = None,
    ) -> Response:
        if not project_config.is_activated_git_workspace():
            return Response(
                content=(
                    "The GIT_WORKSPACE_EXPERIMENTAL feature is not activated in the "
                    "project config."
                ),
                status_code=HTTP_STATUS_PRECONDITION_FAILED,
            )

        status = GitWorkspaceStatusService.get_status(project_config)
        resolved_target_branch = (
            target_branch
            if target_branch is not None and len(target_branch) > 0
            else _default_target_branch(status.branches)
        )

        view_object = GitWorkspaceViewObject(
            project_config=project_config,
            status=status,
            target_branch=resolved_target_branch,
            message=message,
            error_message=error,
        )
        output = view_object.render_screen(html_templates.jinja_environment())
        return HTMLResponse(content=output, status_code=200)

    @router.post("/git_workspace/stage")
    def post_git_workspace_stage(
        target_branch: str = Form(...),
        paths: Optional[List[str]] = Form(None),
    ) -> Response:
        if not project_config.is_activated_git_workspace():
            return Response(status_code=HTTP_STATUS_PRECONDITION_FAILED)

        if paths is None or len(paths) == 0:
            return _redirect_to_git_workspace(
                target_branch, error="Select at least one path to stage."
            )

        git_client = GitClient.open_workspace(project_config)
        with lock_manager.acquire_global_write():
            git_client.stage_paths(paths)
        return _redirect_to_git_workspace(
            target_branch, message="Staged the selected paths."
        )

    @router.post("/git_workspace/commit")
    def post_git_workspace_commit(
        target_branch: str = Form(...),
        message: str = Form(""),
    ) -> Response:
        if not project_config.is_activated_git_workspace():
            return Response(status_code=HTTP_STATUS_PRECONDITION_FAILED)

        if len(message.strip()) == 0:
            return _redirect_to_git_workspace(
                target_branch, error="Commit message must not be empty."
            )

        status = GitWorkspaceStatusService.get_status(project_config)
        if not status.has_staged_changes:
            return _redirect_to_git_workspace(
                target_branch, error="Nothing is staged to commit."
            )

        git_client = GitClient.open_workspace(project_config)
        with lock_manager.acquire_global_write():
            git_client.commit(message)
        return _redirect_to_git_workspace(
            target_branch, message="Committed the staged changes."
        )

    @router.post("/git_workspace/branch")
    def post_git_workspace_branch(
        target_branch: str = Form(...),
        branch_name: str = Form(""),
        action: str = Form(...),
    ) -> Response:
        if not project_config.is_activated_git_workspace():
            return Response(status_code=HTTP_STATUS_PRECONDITION_FAILED)

        if len(branch_name.strip()) == 0:
            return _redirect_to_git_workspace(
                target_branch, error="Branch name must not be empty."
            )

        git_client = GitClient.open_workspace(project_config)
        with lock_manager.acquire_global_write():
            if SyncMergeService.get_active(project_config) is not None:
                return _redirect_to_git_workspace(
                    target_branch,
                    error=(
                        "Finish or abort the in-progress synchronization "
                        "before switching branches."
                    ),
                )
            checkout_result = git_client.checkout_branch(
                branch_name, create=(action == "create")
            )
        if not checkout_result.success:
            return _redirect_to_git_workspace(
                target_branch, error=checkout_result.error_message
            )
        return _redirect_to_git_workspace(
            target_branch, message=f"Switched to branch '{branch_name}'."
        )

    @router.post("/git_workspace/sync")
    def post_git_workspace_sync(
        target_branch: str = Form(...),
        fast_forward: bool = Form(False),
    ) -> Response:
        if not project_config.is_activated_git_workspace():
            return Response(status_code=HTTP_STATUS_PRECONDITION_FAILED)

        # Synchronize is a single custom 3-way structural merge (base =
        # merge_base(target, incoming), target = target branch tip,
        # incoming = this branch's tip) -- never git's own rebase/merge
        # machinery (SDOC-SRS-216). It never commits on its own and never
        # pushes; committing and pushing are separate, explicit actions.
        # Node/section classification always runs in isolated scratch
        # worktrees (SyncMergeService), never on this live working
        # directory.
        #
        # Per SDOC-SRS-217, the left/right review screen is shown by
        # default even when there are zero true conflicts -- the user must
        # explicitly review and commit. The "fast_forward" checkbox is an
        # opt-in escape hatch that restores the old always-auto-publish
        # shortcut, but only when the sync is a clean fast-forward (no true
        # conflicts).
        live_client = GitClient.open_workspace(project_config)
        with lock_manager.acquire_global_write():
            if SyncMergeService.get_active(project_config) is not None:
                return _redirect_to_git_conflicts(
                    target_branch,
                    error=(
                        "A synchronization is already in progress. Resolve "
                        "or abort it first."
                    ),
                )
            if not live_client.is_clean_branch():
                return _redirect_to_git_workspace(
                    target_branch,
                    error=(
                        "Cannot synchronize: the workspace has uncommitted "
                        "changes. Commit them first."
                    ),
                )

            meta, merge_result = SyncMergeService.compute_merge(
                project_config, live_client, target_branch
            )

            if (
                fast_forward
                and merge_result.total_true_conflicts == 0
                and len(meta.non_document_changed_paths) == 0
            ):
                # Opt-in shortcut: publish immediately, no /git_conflicts
                # detour, no state ever persisted. Per SDOC-SRS-224, never
                # taken when either side changed a non-document file --
                # falls through to the normal review-screen path below,
                # which warns and blocks committing instead.
                publish_result = SyncMergeService.materialize_and_publish(
                    project_config, live_client, meta, merge_result
                )
                if not publish_result.success:
                    return _redirect_to_git_workspace(
                        target_branch, error=publish_result.error_message
                    )
                return _redirect_to_git_workspace(
                    target_branch,
                    message=(
                        "Synchronization finished: rebased onto "
                        f"'{target_branch}'."
                    ),
                )

            SyncMergeService.persist(project_config, meta)

        if merge_result.total_true_conflicts == 0:
            return _redirect_to_git_conflicts(
                target_branch,
                message="Synchronization ready. Review and commit below.",
            )
        return _redirect_to_git_conflicts(
            target_branch,
            error=(
                "Synchronization found conflicts. Resolve them below, then "
                "commit."
            ),
        )

    @router.post("/git_workspace/push")
    def post_git_workspace_push(
        target_branch: str = Form(...),
    ) -> Response:
        if not project_config.is_activated_git_workspace():
            return Response(status_code=HTTP_STATUS_PRECONDITION_FAILED)

        git_client = GitClient.open_workspace(project_config)
        with lock_manager.acquire_global_write():
            push_result = git_client.push(
                branch=git_client.get_current_branch()
            )

        if not push_result.success:
            if push_result.rejected_non_fast_forward:
                return _redirect_to_git_workspace(
                    target_branch,
                    error=(
                        "Push rejected (the remote branch has diverged, "
                        "e.g. after a rebase). Use Force push if you are "
                        "sure you want to overwrite it."
                    ),
                )
            return _redirect_to_git_workspace(
                target_branch, error=push_result.error_message
            )

        return _redirect_to_git_workspace(
            target_branch, message="Pushed the branch to its remote."
        )

    @router.post("/git_workspace/force_push")
    def post_git_workspace_force_push(
        target_branch: str = Form(...),
    ) -> Response:
        if not project_config.is_activated_git_workspace():
            return Response(status_code=HTTP_STATUS_PRECONDITION_FAILED)

        git_client = GitClient.open_workspace(project_config)
        with lock_manager.acquire_global_write():
            push_result = git_client.push(
                branch=git_client.get_current_branch(),
                force_with_lease=True,
            )

        if not push_result.success:
            return _redirect_to_git_workspace(
                target_branch, error=push_result.error_message
            )

        return _redirect_to_git_workspace(
            target_branch,
            message="Force-pushed the branch to its remote (--force-with-lease).",
        )

    @router.get("/git_conflicts")
    def get_git_conflicts(
        target_branch: Optional[str] = None,
        message: Optional[str] = None,
        error: Optional[str] = None,
    ) -> Response:
        if not project_config.is_activated_git_workspace():
            return Response(status_code=HTTP_STATUS_PRECONDITION_FAILED)

        live_client = GitClient.open_workspace(project_config)
        meta = SyncMergeService.get_active(project_config)
        merge_result = (
            SyncMergeService.recompute_merge_result(project_config, meta)
            if meta is not None
            else None
        )
        resolved_target_branch = (
            target_branch
            if target_branch is not None and len(target_branch) > 0
            else _default_target_branch(live_client.list_branches())
        )

        view_object = GitConflictsViewObject(
            project_config=project_config,
            merge_result=merge_result,
            allocations=meta.allocations if meta is not None else {},
            placements=meta.placements if meta is not None else {},
            non_document_changed_paths=(
                meta.non_document_changed_paths if meta is not None else []
            ),
            target_branch=resolved_target_branch,
            message=message,
            error_message=error,
        )
        output = view_object.render_screen(html_templates.jinja_environment())
        return HTMLResponse(content=output, status_code=200)

    @router.post("/git_conflicts/resolve_node")
    def post_git_conflicts_resolve_node(
        target_branch: str = Form(...),
        node_key: str = Form(...),
        decision: str = Form(...),
    ) -> Response:
        if not project_config.is_activated_git_workspace():
            return Response(status_code=HTTP_STATUS_PRECONDITION_FAILED)
        if decision not in ("target", "incoming"):
            return _redirect_to_git_conflicts(
                target_branch, error="Invalid side to resolve with."
            )

        with lock_manager.acquire_global_write():
            meta = SyncMergeService.get_active(project_config)
            if meta is None:
                return _redirect_to_git_conflicts(
                    target_branch,
                    error="No synchronization is currently in progress.",
                )
            merge_result = SyncMergeService.recompute_merge_result(
                project_config, meta
            )
            node_result = merge_result.find_node_result(node_key)
            if node_result is None or not node_result.is_conflict():
                return _redirect_to_git_conflicts(
                    target_branch, error="Unknown or already-resolved node."
                )
            SyncMergeService.allocate(
                project_config, meta, merge_result, node_key, decision
            )

        return _redirect_to_git_conflicts(
            target_branch, message="Node resolved."
        )

    @router.post("/git_conflicts/place_node")
    def post_git_conflicts_place_node(
        target_branch: str = Form(...),
        node_key: str = Form(...),
        after_key: str = Form(...),
    ) -> Response:
        if not project_config.is_activated_git_workspace():
            return Response(status_code=HTTP_STATUS_PRECONDITION_FAILED)

        with lock_manager.acquire_global_write():
            meta = SyncMergeService.get_active(project_config)
            if meta is None:
                return _redirect_to_git_conflicts(
                    target_branch,
                    error="No synchronization is currently in progress.",
                )
            merge_result = SyncMergeService.recompute_merge_result(
                project_config, meta
            )
            node_result = merge_result.find_node_result(node_key)
            if (
                node_result is None
                or node_result.base_node is not None
                or node_result.is_conflict()
            ):
                return _redirect_to_git_conflicts(
                    target_branch,
                    error="This node cannot be repositioned.",
                )
            if after_key != PLACEMENT_START:
                after_result = merge_result.find_node_result(after_key)
                if after_result is None:
                    return _redirect_to_git_conflicts(
                        target_branch, error="Unknown drop target."
                    )
                document_result = merge_result.find_document_result(node_key)
                assert document_result is not None
                parent_key_of = compute_parent_key_map(document_result)
                if parent_key_of.get(node_key) != parent_key_of.get(after_key):
                    return _redirect_to_git_conflicts(
                        target_branch,
                        error="Can only reposition among sibling nodes.",
                    )
            SyncMergeService.place_after(
                project_config, meta, merge_result, node_key, after_key
            )

        return _redirect_to_git_conflicts(
            target_branch, message="Node repositioned."
        )

    @router.post("/git_conflicts/resolve_section")
    def post_git_conflicts_resolve_section(
        target_branch: str = Form(...),
        section_key: str = Form(...),
        decision: str = Form(...),
    ) -> Response:
        if not project_config.is_activated_git_workspace():
            return Response(status_code=HTTP_STATUS_PRECONDITION_FAILED)
        if decision not in ("target", "incoming"):
            return _redirect_to_git_conflicts(
                target_branch, error="Invalid side to resolve with."
            )

        with lock_manager.acquire_global_write():
            meta = SyncMergeService.get_active(project_config)
            if meta is None:
                return _redirect_to_git_conflicts(
                    target_branch,
                    error="No synchronization is currently in progress.",
                )
            merge_result = SyncMergeService.recompute_merge_result(
                project_config, meta
            )
            section_result = merge_result.find_node_result(section_key)
            if section_result is None:
                return _redirect_to_git_conflicts(
                    target_branch, error="Unknown section."
                )
            SyncMergeService.allocate_section(
                project_config, meta, merge_result, section_key, decision
            )

        return _redirect_to_git_conflicts(
            target_branch, message="Section resolved."
        )

    @router.post("/git_conflicts/commit")
    def post_git_conflicts_commit(
        target_branch: str = Form(...),
    ) -> Response:
        if not project_config.is_activated_git_workspace():
            return Response(status_code=HTTP_STATUS_PRECONDITION_FAILED)

        live_client = GitClient.open_workspace(project_config)
        with lock_manager.acquire_global_write():
            meta = SyncMergeService.get_active(project_config)
            if meta is None:
                return _redirect_to_git_conflicts(
                    target_branch,
                    error="No synchronization is currently in progress.",
                )
            merge_result = SyncMergeService.recompute_merge_result(
                project_config, meta
            )
            if not SyncMergeService.is_fully_resolved(merge_result, meta):
                return _redirect_to_git_conflicts(
                    target_branch,
                    error="Resolve all conflicts before committing.",
                )
            if len(meta.non_document_changed_paths) > 0:
                # SDOC-SRS-224: synchronization only merges document
                # content through the 3-way classifier -- committing while
                # a non-document file changed on either side would take it
                # from target alone or drop it entirely.
                return _redirect_to_git_conflicts(
                    target_branch,
                    error=(
                        "Cannot commit: the branches being synchronized "
                        "change files that are not in a readable StrictDoc "
                        "format. Resolve these outside StrictDoc first."
                    ),
                )
            publish_result = SyncMergeService.materialize_and_publish(
                project_config, live_client, meta, merge_result
            )

        if not publish_result.success:
            return _redirect_to_git_conflicts(
                target_branch, error=publish_result.error_message
            )

        return _redirect_to_git_workspace(
            target_branch,
            message=(
                "Synchronization finished: rebased onto "
                f"'{target_branch}'. Synchronize again if needed, or push "
                "when ready."
            ),
        )

    @router.post("/git_conflicts/abort")
    def post_git_conflicts_abort(
        target_branch: str = Form(...),
    ) -> Response:
        if not project_config.is_activated_git_workspace():
            return Response(status_code=HTTP_STATUS_PRECONDITION_FAILED)

        with lock_manager.acquire_global_write():
            SyncMergeService.cleanup(project_config)

        return _redirect_to_git_workspace(
            target_branch, message="Synchronization aborted."
        )

    return router
