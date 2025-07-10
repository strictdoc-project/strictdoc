from typing import Any, List, Optional

from strictdoc.backend.sdoc.models.document import SDocDocument
from strictdoc.backend.sdoc.models.document_grammar import (
    DocumentGrammar,
)
from strictdoc.backend.sdoc.models.grammar_element import GrammarElement
from strictdoc.backend.sdoc.models.model import SDocElementIF
from strictdoc.backend.sdoc.models.node import SDocNode, SDocNodeField
from strictdoc.backend.sdoc.models.section import SDocSection
from strictdoc.core.traceability_index import TraceabilityIndex
from strictdoc.helpers.cast import assert_cast


class Expression:
    pass


class StringExpression:
    def __init__(self, parent: Any, string: str):
        self.parent: Any = parent
        self.string: str = string


class NoneExpression:
    def __init__(self, parent: Any, _: str):
        self.parent: Any = parent


class NodeFieldExpression:
    def __init__(self, parent: Any, field_name: str):
        self.parent: Any = parent
        self.field_name = field_name


class NodeContainsExpression:
    def __init__(self, parent: Any, string: str):
        self.parent: Any = parent
        self.string: str = string


class NodeHasParentRequirementsExpression:
    def __init__(self, parent: Any, _: Any) -> None:
        self.parent: Any = parent


class NodeContainsAnyFreeTextExpression:
    def __init__(self, parent: Any, _: Any):
        self.parent: Any = parent


class NodeHasChildRequirementsExpression:
    def __init__(self, parent: Any, _: Any):
        self.parent: Any = parent


class NodeIsRequirementExpression:
    def __init__(self, parent: Any, _: Any):
        self.parent: Any = parent


class NodeIsSectionExpression:
    def __init__(self, parent: Any, _: Any):
        self.parent: Any = parent


class NodeIsRootExpression:
    def __init__(self, parent: Any, _: Any):
        self.parent: Any = parent


class EqualExpression:
    def __init__(self, parent: Any, lhs_expr: Expression, rhs_expr: Expression):
        self.parent: Any = parent
        self.lhs_expr: Expression = lhs_expr
        self.rhs_expr: Expression = rhs_expr


class AndExpression:
    def __init__(self, parent: Any, expressions: List[Expression]):
        self.parent: Any = parent
        self.expressions: List[Expression] = expressions


class OrExpression:
    def __init__(self, parent: Any, expressions: List[Expression]):
        self.parent: Any = parent
        self.expressions: List[Expression] = expressions


class NotExpression:
    def __init__(self, parent: Any, expression: Expression):
        self.parent: Any = parent
        self.expression: Expression = expression


class NotEqualExpression:
    def __init__(self, parent: Any, lhs_expr: Expression, rhs_expr: Expression):
        self.parent: Any = parent
        self.lhs_expr: Expression = lhs_expr
        self.rhs_expr: Expression = rhs_expr


class InExpression:
    def __init__(self, parent: Any, lhs_expr: Expression, rhs_expr: Expression):
        self.parent: Any = parent
        self.lhs_expr: Expression = lhs_expr
        self.rhs_expr: Expression = rhs_expr


class NotInExpression:
    def __init__(self, parent: Any, lhs_expr: Expression, rhs_expr: Expression):
        self.parent: Any = parent
        self.lhs_expr: Expression = lhs_expr
        self.rhs_expr: Expression = rhs_expr


class Query:
    def __init__(self, root_expression: Any):
        self.root_expression: Any = root_expression


class QueryNullObject:
    def evaluate(self, _: Any) -> bool:
        return True


class QueryObject:
    def __init__(
        self, query: Query, traceability_index: TraceabilityIndex
    ) -> None:
        self.query: Query = query
        self.traceability_index: TraceabilityIndex = traceability_index

    def evaluate(self, node: SDocElementIF) -> bool:
        return self._evaluate(node, self.query.root_expression)

    def _evaluate(self, node: SDocElementIF, expression: Any) -> bool:
        if isinstance(expression, EqualExpression):
            return self._evaluate_equal(node, expression)
        if isinstance(expression, NotEqualExpression):
            return self._evaluate_not_equal(node, expression)
        if isinstance(expression, NodeContainsExpression):
            return self._evaluate_node_contains(node, expression)
        if isinstance(expression, NodeContainsAnyFreeTextExpression):
            return self._evaluate_node_contains_any_text(node)
        if isinstance(expression, NodeHasParentRequirementsExpression):
            return self._evaluate_node_has_parent_requirements(node)
        if isinstance(expression, NodeHasChildRequirementsExpression):
            return self._evaluate_node_has_child_requirements(node)
        if isinstance(expression, NodeIsRequirementExpression):
            return (
                isinstance(node, SDocNode) and node.node_type == "REQUIREMENT"
            )
        if isinstance(expression, NodeIsSectionExpression):
            return (
                isinstance(node, SDocNode) and node.node_type == "SECTION"
            ) or isinstance(node, SDocSection)
        if isinstance(expression, NodeIsRootExpression):
            if isinstance(node, SDocNode):
                return node.is_root
            raise RuntimeError(
                "The node.is_root expression can be only called on nodes."
            )
        if isinstance(expression, NotExpression):
            return not self._evaluate(node, expression.expression)
        if isinstance(expression, AndExpression):
            for sub_expression_ in expression.expressions:
                if not self._evaluate(node, sub_expression_):
                    return False
            return True
        if isinstance(expression, OrExpression):
            for sub_expression_ in expression.expressions:
                if self._evaluate(node, sub_expression_):
                    return True
            return False
        if isinstance(expression, InExpression):
            if (
                rhs_value := self._evaluate_value(node, expression.rhs_expr)
            ) is not None and (
                lhs_value := self._evaluate_value(node, expression.lhs_expr)
            ) is not None:
                return lhs_value in rhs_value
            return False
        if isinstance(expression, NotInExpression):
            if (
                rhs_value := self._evaluate_value(node, expression.rhs_expr)
            ) is not None and (
                lhs_value := self._evaluate_value(node, expression.lhs_expr)
            ) is not None:
                return lhs_value not in rhs_value
            return False
        assert 0, expression

    def _evaluate_equal(
        self, node: SDocElementIF, expression: EqualExpression
    ) -> bool:
        return self._evaluate_value(
            node, expression.lhs_expr
        ) == self._evaluate_value(node, expression.rhs_expr)

    def _evaluate_not_equal(
        self, node: SDocElementIF, expression: NotEqualExpression
    ) -> bool:
        return self._evaluate_value(
            node, expression.lhs_expr
        ) != self._evaluate_value(node, expression.rhs_expr)

    def _evaluate_value(
        self, node: SDocElementIF, expression: Any
    ) -> Optional[str]:
        if isinstance(expression, NodeFieldExpression):
            return self._evaluate_node_field_expression(node, expression)
        if isinstance(expression, StringExpression):
            return expression.string
        if isinstance(expression, NoneExpression):
            return None
        assert 0, expression

    def _evaluate_node_field_expression(
        self,
        node: SDocElementIF,
        expression: NodeFieldExpression,
    ) -> Optional[str]:
        field_name = expression.field_name
        if (
            isinstance(node, SDocNode)
            and node.is_requirement()
            and node.node_type == "REQUIREMENT"
        ):
            requirement: SDocNode = assert_cast(node, SDocNode)
            requirement_document: SDocDocument = assert_cast(
                requirement.get_document(), SDocDocument
            )
            document_grammar: DocumentGrammar = assert_cast(
                requirement_document.grammar, DocumentGrammar
            )
            element: GrammarElement = document_grammar.elements_by_type[
                requirement.node_type
            ]
            grammar_field_titles = list(map(lambda f: f.title, element.fields))
            if field_name not in grammar_field_titles:
                return None
            field_value = requirement._get_cached_field(field_name, False)
            if field_value is not None:
                return field_value
            return None
        elif isinstance(node, SDocSection) and node.is_section():
            section: SDocSection = assert_cast(node, SDocSection)
            if field_name == "UID":
                return section.reserved_uid
            elif field_name == "TITLE":
                return section.title
            raise AttributeError(f"No such section field: {field_name}.")
        else:
            raise NotImplementedError

    def _evaluate_node_has_parent_requirements(
        self, node: SDocElementIF
    ) -> bool:
        if not isinstance(node, SDocNode):
            raise TypeError(
                f"node.has_parent_requirements can be only called on "
                f"Requirement objects, got: {node.__class__.__name__}. To fix "
                f"the error, prepend your query with node.is_requirement."
            )
        return self.traceability_index.has_parent_requirements(node)

    def _evaluate_node_has_child_requirements(
        self, node: SDocElementIF
    ) -> bool:
        if not isinstance(node, SDocNode):
            raise TypeError(
                f"node.has_child_requirements can be only called on "
                f"Requirement objects, got: {node.__class__.__name__}. To fix "
                f"the error, prepend your query with node.is_requirement."
            )
        return self.traceability_index.has_children_requirements(node)

    def _evaluate_node_contains(
        self,
        node: SDocElementIF,
        expression: NodeContainsExpression,
    ) -> bool:
        if isinstance(node, SDocNode):
            requirement = assert_cast(node, SDocNode)
            requirement_field_: SDocNodeField
            for requirement_field_ in requirement.enumerate_fields():
                if expression.string in requirement_field_.get_text_value():
                    return True
            return False
        if isinstance(node, SDocSection):
            section = assert_cast(node, SDocSection)
            if expression.string in section.title:
                return True
            return False
        raise NotImplementedError

    def _evaluate_node_contains_any_text(self, node: SDocElementIF) -> bool:
        if not isinstance(node, SDocSection) and not (
            isinstance(node, SDocNode) and node.node_type == "SECTION"
        ):
            raise TypeError(
                f"node.contains_any_text can be only called on "
                f"SECTION objects, got: {node.__class__.__name__}. To fix "
                f"the error, prepend your query with node.is_section."
            )
        return node.has_any_text_nodes()
