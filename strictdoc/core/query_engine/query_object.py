# mypy: disable-error-code="no-any-return,no-untyped-call,no-untyped-def,union-attr,operator"
from typing import List, Optional

from strictdoc.backend.sdoc.models.document_grammar import GrammarElement
from strictdoc.backend.sdoc.models.node import SDocNode, SDocNodeField
from strictdoc.backend.sdoc.models.section import SDocSection
from strictdoc.core.traceability_index import TraceabilityIndex
from strictdoc.helpers.cast import assert_cast


class Expression:
    pass


class StringExpression:
    def __init__(self, parent, string: str):
        self.parent = parent
        self.string: str = string


class NoneExpression:
    def __init__(self, parent, _: str):
        self.parent = parent


class NodeFieldExpression:
    def __init__(self, parent, field_name: str):
        self.parent = parent
        self.field_name = field_name


class NodeContainsExpression:
    def __init__(self, parent, string: str):
        self.parent = parent
        self.string: str = string


class NodeHasParentRequirementsExpression:
    def __init__(self, parent, _):
        self.parent = parent


class NodeContainsAnyFreeTextExpression:
    def __init__(self, parent, _):
        self.parent = parent


class NodeHasChildRequirementsExpression:
    def __init__(self, parent, _):
        self.parent = parent


class NodeIsRequirementExpression:
    def __init__(self, parent, _):
        self.parent = parent


class NodeIsSectionExpression:
    def __init__(self, parent, _):
        self.parent = parent


class NodeIsRootExpression:
    def __init__(self, parent, _):
        self.parent = parent


class EqualExpression:
    def __init__(self, parent, lhs_expr: Expression, rhs_expr: Expression):
        self.parent = parent
        self.lhs_expr: Expression = lhs_expr
        self.rhs_expr: Expression = rhs_expr


class AndExpression:
    def __init__(self, parent, expressions: List[Expression]):
        self.parent = parent
        self.expressions: List[Expression] = expressions


class OrExpression:
    def __init__(self, parent, expressions: List[Expression]):
        self.parent = parent
        self.expressions: List[Expression] = expressions


class NotExpression:
    def __init__(self, parent, expression: Expression):
        self.parent = parent
        self.expression: Expression = expression


class NotEqualExpression:
    def __init__(self, parent, lhs_expr: Expression, rhs_expr: Expression):
        self.parent = parent
        self.lhs_expr: Expression = lhs_expr
        self.rhs_expr: Expression = rhs_expr


class InExpression:
    def __init__(self, parent, lhs_expr: Expression, rhs_expr: Expression):
        self.parent = parent
        self.lhs_expr: Expression = lhs_expr
        self.rhs_expr: Expression = rhs_expr


class NotInExpression:
    def __init__(self, parent, lhs_expr: Expression, rhs_expr: Expression):
        self.parent = parent
        self.lhs_expr: Expression = lhs_expr
        self.rhs_expr: Expression = rhs_expr


class Query:
    def __init__(self, root_expression):
        self.root_expression = root_expression


class QueryNullObject:
    def evaluate(self, _) -> bool:
        return True


class QueryObject:
    def __init__(self, query: Query, traceability_index: TraceabilityIndex):
        self.query: Query = query
        self.traceability_index: TraceabilityIndex = traceability_index

    def evaluate(self, node) -> bool:
        return self._evaluate(node, self.query.root_expression)

    def _evaluate(self, node, expression) -> bool:
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
            return isinstance(node, SDocSection)
        if isinstance(expression, NodeIsRootExpression):
            return node.is_root
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
            rhs_value = self._evaluate_value(node, expression.rhs_expr)
            if rhs_value is None:
                return False
            return self._evaluate_value(node, expression.lhs_expr) in rhs_value
        if isinstance(expression, NotInExpression):
            rhs_value = self._evaluate_value(node, expression.rhs_expr)
            if rhs_value is None:
                return False
            return (
                self._evaluate_value(node, expression.lhs_expr) not in rhs_value
            )
        assert 0, expression

    def _evaluate_equal(self, node, expression: EqualExpression) -> bool:
        return self._evaluate_value(
            node, expression.lhs_expr
        ) == self._evaluate_value(node, expression.rhs_expr)

    def _evaluate_not_equal(self, node, expression: NotEqualExpression) -> bool:
        return self._evaluate_value(
            node, expression.lhs_expr
        ) != self._evaluate_value(node, expression.rhs_expr)

    def _evaluate_value(self, node, expression) -> Optional[str]:
        if isinstance(expression, NodeFieldExpression):
            return self._evaluate_node_field_expression(node, expression)
        if isinstance(expression, StringExpression):
            return expression.string
        if isinstance(expression, NoneExpression):
            return None
        assert 0, expression

    def _evaluate_node_field_expression(
        self, node, expression: NodeFieldExpression
    ) -> Optional[str]:
        field_name = expression.field_name
        if node.is_requirement:
            requirement: SDocNode = assert_cast(node, SDocNode)
            element: GrammarElement = (
                requirement.document.grammar.elements_by_type[
                    requirement.node_type
                ]
            )
            grammar_field_titles = list(map(lambda f: f.title, element.fields))
            if field_name not in grammar_field_titles:
                return None
            field_value = requirement._get_cached_field(field_name, False)
            if field_value is not None:
                return field_value
            return None
        elif node.is_section:
            section: SDocSection = assert_cast(node, SDocSection)
            if field_name == "UID":
                return section.reserved_uid
            elif field_name == "TITLE":
                return section.title
            raise AttributeError(f"No such section field: {field_name}.")
        else:
            raise NotImplementedError

    def _evaluate_node_has_parent_requirements(self, node):
        if not isinstance(node, SDocNode):
            raise TypeError(
                f"node.has_parent_requirements can be only called on "
                f"Requirement objects, got: {node.__class__.__name__}. To fix "
                f"the error, prepend your query with node.is_requirement."
            )
        return self.traceability_index.has_parent_requirements(node)

    def _evaluate_node_has_child_requirements(self, node):
        if not isinstance(node, SDocNode):
            raise TypeError(
                f"node.has_child_requirements can be only called on "
                f"Requirement objects, got: {node.__class__.__name__}. To fix "
                f"the error, prepend your query with node.is_requirement."
            )
        return self.traceability_index.has_children_requirements(node)

    def _evaluate_node_contains(
        self, node, expression: NodeContainsExpression
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

    def _evaluate_node_contains_any_text(self, node):
        if not isinstance(node, SDocSection):
            raise TypeError(
                f"node.contains_any_text can be only called on "
                f"Section objects, got: {node.__class__.__name__}. To fix "
                f"the error, prepend your query with node.is_section."
            )
        return len(node.free_texts) > 0
