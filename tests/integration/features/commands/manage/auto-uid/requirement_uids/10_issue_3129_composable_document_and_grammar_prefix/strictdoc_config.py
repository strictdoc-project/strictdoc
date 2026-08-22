from typing import Optional, Union

from strictdoc.api import (
    GrammarElement,
    ProjectConfig,
    SDocDocument,
    SDocNode,
    TraceabilityIndex,
)


# Reproduces the composable-prefix algorithm requested in
# https://github.com/strictdoc-project/strictdoc/issues/3129.
def custom_node_prefix(
    node: Union[SDocNode, SDocDocument],  # noqa: ARG001
    grammar_element: GrammarElement,
    document: SDocDocument,
    traceability_index: TraceabilityIndex,  # noqa: ARG001
    project_config: ProjectConfig,  # noqa: ARG001
) -> Optional[str]:
    document_prefix = document.config.requirement_prefix
    grammar_prefix = grammar_element.property_prefix
    if document_prefix and grammar_prefix:
        return f"{document_prefix}{grammar_prefix}"
    if grammar_prefix:
        return grammar_prefix
    if document_prefix:
        return document_prefix
    return None


def create_config() -> ProjectConfig:
    return ProjectConfig(
        project_title="Test Project",
        custom_node_prefix_function=custom_node_prefix,
    )
