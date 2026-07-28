from strictdoc.core.project_config import ProjectConfig


def create_config() -> ProjectConfig:
    config = ProjectConfig(
        project_title="Stable URL Links Test (chunked)",
        # The fixture document has 35 requirements, and a threshold of 10
        # forces chunking with chunk size 10 (4 chunks: 0-9, 10-19, 20-29,
        # 30-34). Each chunk's real/estimated height must comfortably
        # exceed the viewport plus toc_chunk_navigation.js's 800px preload
        # margin on each side, or intermediate chunks preload just for
        # being numerically close to the target - these values (matching
        # tests/end2end/screens/document/lazy_loading) are large enough
        # for that. The test itself still asserts the target chunk is
        # unloaded before navigating, rather than relying on this comment
        # alone.
        chunked_documents_threshold=10,
    )
    return config
