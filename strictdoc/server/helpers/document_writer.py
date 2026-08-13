from fastapi import FastAPI

from strictdoc.backend.markdown.writer import SDMarkdownWriter
from strictdoc.backend.sdoc.models.document import SDocDocument
from strictdoc.backend.sdoc.writer import SDWriter
from strictdoc.core.project_config import ProjectConfig


class DocumentWriter:
    """
    Reserializes an in-memory SDocDocument tree back to its file on disk.

    FIXME: The writer dispatch below is hardcoded to ".md"/".markdown" vs.
    everything else, not derived from project_config.formats /
    Format.supports_edit(). Document creation now accepts any editable
    format's extension (see ProjectConfig.get_editable_document_extensions()),
    so a third editable format would pass creation validation but get
    silently mis-written here.
    """

    def __init__(self, *, project_config: ProjectConfig, app: FastAPI) -> None:
        self.project_config: ProjectConfig = project_config
        self.app: FastAPI = app
        self.sdoc_writer: SDWriter = SDWriter(project_config)

    def write_document_to_file(self, document: SDocDocument) -> None:
        assert isinstance(document, SDocDocument)

        # Inhibit before writing so the watcher's debounce always fires into
        # an already-suppressed state -- no race window between write and
        # hash.
        if document.meta is not None:
            document_watcher = getattr(self.app.state, "document_watcher", None)
            if document_watcher is not None:
                document_watcher.inhibit_next_change(
                    document.meta.input_doc_full_path
                )

        if (
            document.meta is not None
            and document.meta.input_doc_full_path.lower().endswith(
                (".md", ".markdown")
            )
        ):
            SDMarkdownWriter.write_to_file(
                document, line_width=self.project_config.document_line_width
            )
        else:
            self.sdoc_writer.write_to_file(document)
