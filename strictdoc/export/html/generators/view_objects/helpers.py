from strictdoc.core.file_tree import File, Folder
from strictdoc.core.project_config import ProjectConfig
from strictdoc.core.traceability_index import TraceabilityIndex


def screen_should_display_folder(
    folder: Folder,
    traceability_index: TraceabilityIndex,
    project_config: ProjectConfig,
    must_only_include_non_included_sdoc: bool,
) -> bool:
    """
    Control if a folder appears on Project Index or Document screen.

    must_only_include_non_included_sdoc:
        see screen_should_display_file() for a description of the purpose.
    """
    assert isinstance(folder, Folder), folder
    assert traceability_index.document_tree is not None

    if not folder.has_sdoc_content:
        return False

    for file_ in folder.files:
        if screen_should_display_file(
            file_,
            traceability_index,
            project_config,
            must_only_include_non_included_sdoc,
        ):
            return True

    for folder_ in folder.subfolder_trees:
        if screen_should_display_folder(
            folder_,
            traceability_index,
            project_config,
            must_only_include_non_included_sdoc,
        ):
            return True

    return False


def screen_should_display_file(
    file: File,
    traceability_index: TraceabilityIndex,
    project_config: ProjectConfig,
    must_only_include_non_included_sdoc: bool,
) -> bool:
    """
    Control if a file appears on Project Index or Document screen.

    must_only_include_non_included_sdoc:
        the argument controls whether to only display non-included SDoc
        documents or also included (fragment) documents. The Project Tree screen
        uses this as False while Document screen uses it as False where the
        standalone fragments are not printed, and instead the including documents
        prints its included documents recursively.
    """
    assert isinstance(file, File), file
    assert traceability_index.document_tree is not None

    if (
        file.has_extension(".junit.xml")
        or file.has_extension(".gcov.json")
        or file.has_extension(".robot.xml")
    ):
        return True

    if file.has_extension(".sdoc"):
        document = traceability_index.document_tree.get_document_by_path(
            file.full_path
        )
        if not document.document_is_included():
            return True

        if (
            not must_only_include_non_included_sdoc
            and project_config.export_included_documents
        ):
            return True

    return False
