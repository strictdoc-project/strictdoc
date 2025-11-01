from typing import Dict, List, Optional, Union

from strictdoc.backend.sdoc.models.model import (
    SDocDocumentIF,
    SDocNodeIF,
)


class ValidationIndex:
    def __init__(self) -> None:
        self.node_issues: Dict[
            Union[SDocNodeIF, SDocDocumentIF], Dict[Optional[str], List[str]]
        ] = {}

    def add_issue(
        self,
        node: Union[SDocNodeIF, SDocDocumentIF],
        issue: str,
        field: Optional[str] = None,
        subject: Optional[str] = None,
    ) -> None:
        self.node_issues.setdefault(node, {}).setdefault(field, []).append(
            issue
        )

        if isinstance(node, SDocNodeIF):
            document_node = node.get_parent_or_including_document()
            self.node_issues.setdefault(document_node, {}).setdefault(
                None, []
            ).append(issue)

        print_issue = issue
        if subject is not None:
            print_issue = f"{issue} {subject}"
        print(f"warning: {print_issue}")  # noqa: T201

    def get_issues(
        self,
        node: Union[SDocNodeIF, SDocDocumentIF],
        field: Optional[str] = None,
    ) -> Optional[List[str]]:
        if node not in self.node_issues:
            return None
        node_issues = self.node_issues[node]
        if field not in node_issues:
            return None
        issues = node_issues[field]
        if isinstance(node, SDocDocumentIF) and not node.document_is_included():
            return [f"Document has {len(issues)} issues."]
        return issues
