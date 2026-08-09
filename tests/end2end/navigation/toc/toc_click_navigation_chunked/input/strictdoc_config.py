from strictdoc.core.project_config import ProjectConfig


def create_config() -> ProjectConfig:
    config = ProjectConfig(
        project_title="TOC Click Navigation Chunked Test",
        # The fixture document has 14 content nodes. A threshold of 5 forces
        # chunking (chunk size = min(threshold, 100) = 5), and puts
        # SECTION_BEFORE_LONG_NODE (the 5th node) as the last node of chunk 0,
        # which is always rendered inline - i.e., already in the DOM without
        # any lazy chunk needing to be force-loaded. This isolates the
        # "target already in the DOM" branch of TOC click navigation under
        # chunking, as opposed to the force-load branch already covered by
        # tests/end2end/navigation/toc/toc_highlighting_lazy_chunks.
        lazy_document_loading_threshold=5,
    )
    return config
