from typing import Optional, Union

from strictdoc.api import (
    GrammarElement,
    ProjectConfig,
    SDocDocument,
    SDocNode,
    TraceabilityIndex,
)


def custom_node_prefix(
    node: Union[SDocNode, SDocDocument],  # noqa: ARG001
    grammar_element: GrammarElement,  # noqa: ARG001
    document: SDocDocument,
    traceability_index: TraceabilityIndex,  # noqa: ARG001
    project_config: ProjectConfig,  # noqa: ARG001
) -> Optional[str]:
    if document.reserved_uid == "MY_UID":
        return "MY_UID_PREFIX-"
    # Revert to the default behavior.
    return None


def create_config() -> ProjectConfig:
    return ProjectConfig(
        project_title="Test Project",
        custom_node_prefix_function=custom_node_prefix,
    )
