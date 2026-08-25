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
    document: SDocDocument,  # noqa: ARG001
    traceability_index: TraceabilityIndex,  # noqa: ARG001
    project_config: ProjectConfig,  # noqa: ARG001
) -> Optional[str]:
    return "CUSTOM-"


def create_config() -> ProjectConfig:
    return ProjectConfig(
        project_title="Test Project",
        custom_node_prefix_function=custom_node_prefix,
    )
