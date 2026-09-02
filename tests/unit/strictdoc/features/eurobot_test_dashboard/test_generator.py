"""
@relation(SDOC-SRS-97, scope=file)
"""

from typing import Dict, List

from strictdoc.backend.sdoc.reader import SDReader
from strictdoc.core.document_tree import DocumentTree
from strictdoc.core.project_config import ProjectConfig
from strictdoc.core.traceability_index import TraceabilityIndex
from strictdoc.core.traceability_index_builder import TraceabilityIndexBuilder
from strictdoc.export.html.renderers.link_renderer import LinkRenderer
from strictdoc.features.eurobot_test_dashboard.generator import (
    EurobotTestDashboardGenerator,
)
from strictdoc.features.eurobot_test_dashboard.models import DashboardScope
from tests.unit.helpers.fake_document_meta import create_fake_document_meta

# A trimmed stand-in for eurobot/eurobot_grammar.sgra: same three elements
# and field shape (UID/TITLE/[STATUS|TARGET_REVISION]/STATEMENT plus a
# Parent relation), just inlined so this test has no dependency on the
# eurobot/ reference project's own grammar file.
EUROBOT_TEST_GRAMMAR = """
[GRAMMAR]
ELEMENTS:
- TAG: RULE
  FIELDS:
  - TITLE: UID
    TYPE: String
    REQUIRED: True
  - TITLE: TITLE
    TYPE: String
    REQUIRED: False
  - TITLE: STATUS
    TYPE: SingleChoice(Active, Removed)
    REQUIRED: True
  - TITLE: STATEMENT
    TYPE: String
    REQUIRED: True
- TAG: REQUIREMENT
  FIELDS:
  - TITLE: UID
    TYPE: String
    REQUIRED: True
  - TITLE: TITLE
    TYPE: String
    REQUIRED: False
  - TITLE: TARGET_REVISION
    TYPE: SingleChoice(C1, C2)
    REQUIRED: True
  - TITLE: STATEMENT
    TYPE: String
    REQUIRED: True
  RELATIONS:
  - TYPE: Parent
    ROLE: COVERS
- TAG: TEST_CASE
  FIELDS:
  - TITLE: UID
    TYPE: String
    REQUIRED: True
  - TITLE: TITLE
    TYPE: String
    REQUIRED: False
  - TITLE: STATUS
    TYPE: SingleChoice(Not Executed, Blocked, Failed, Passed)
    REQUIRED: True
  - TITLE: STATEMENT
    TYPE: String
    REQUIRED: True
  RELATIONS:
  - TYPE: Parent
    ROLE: VERIFIES
""".strip()

# Deliberately builds one gap of each kind:
#   RULE-2         -> no covering requirement                  (gap 1)
#   REQ-2          -> covers no rule                            (gap 2)
#   REQ-3          -> covered by RULE-1, but no verifying test   (gap 3)
#   TC-2           -> verifies REQ-2, STATUS Not Executed        (gap 4)
# REQ-1/TC-1 are fully covered/verified/Passed, so they should never appear
# in any gap. REQ-4 carries TARGET_REVISION: TBD, to exercise the
# "no defined scope position" path.
EUROBOT_TEST_DOCUMENT = (
    """
[DOCUMENT]
TITLE: Test Document

"""
    + EUROBOT_TEST_GRAMMAR
    + """

[RULE]
UID: RULE-1
TITLE: Rule one
STATUS: Active
STATEMENT: Rule one statement.

[RULE]
UID: RULE-2
TITLE: Rule two
STATUS: Active
STATEMENT: Rule two statement.

[REQUIREMENT]
UID: REQ-1
TITLE: Requirement one
TARGET_REVISION: C1
STATEMENT: Requirement one statement.
RELATIONS:
- TYPE: Parent
  VALUE: RULE-1
  ROLE: COVERS

[REQUIREMENT]
UID: REQ-2
TITLE: Requirement two
TARGET_REVISION: C2
STATEMENT: Requirement two statement.

[REQUIREMENT]
UID: REQ-3
TITLE: Requirement three
TARGET_REVISION: C1
STATEMENT: Requirement three statement.
RELATIONS:
- TYPE: Parent
  VALUE: RULE-1
  ROLE: COVERS

[REQUIREMENT]
UID: REQ-4
TITLE: Requirement four
TARGET_REVISION: TBD
STATEMENT: Requirement four statement.

[TEST_CASE]
UID: TC-1
TITLE: Test one
STATUS: Passed
STATEMENT: Test one statement.
RELATIONS:
- TYPE: Parent
  VALUE: REQ-1
  ROLE: VERIFIES

[TEST_CASE]
UID: TC-2
TITLE: Test two
STATUS: Not Executed
STATEMENT: Test two statement.
RELATIONS:
- TYPE: Parent
  VALUE: REQ-2
  ROLE: VERIFIES
"""
).lstrip()


def _build_traceability_index() -> TraceabilityIndex:
    document = SDReader().read(EUROBOT_TEST_DOCUMENT)
    document.meta = create_fake_document_meta()

    document_tree = DocumentTree(
        file_tree=[],
        document_list=[document],
        map_docs_by_paths={},
        map_docs_by_rel_paths={},
        map_grammars_by_filenames={},
    )
    return TraceabilityIndexBuilder.create_from_document_tree(
        document_tree, project_config=ProjectConfig.default_config()
    )


def _scopes_by_key(scopes: List[DashboardScope]) -> Dict[str, DashboardScope]:
    return {scope_.key: scope_ for scope_ in scopes}


def _gap_uids(scope: DashboardScope, gap_index: int) -> List[str]:
    return [item_.uid for item_ in scope.gaps[gap_index].items]


def test_unscoped_gaps_cover_all_four_checks():
    traceability_index = _build_traceability_index()
    link_renderer = LinkRenderer(root_path="", static_path="_assets")

    scopes = EurobotTestDashboardGenerator.compute_scopes(
        traceability_index, link_renderer
    )
    scopes_by_key = _scopes_by_key(scopes)
    all_scope = scopes_by_key["all"]

    # Gap 1: RULE-2 has no covering REQUIREMENT; RULE-1 is covered.
    assert _gap_uids(all_scope, 0) == ["RULE-2"]

    # Gap 2: REQ-2 covers no RULE; REQ-1/REQ-3 cover RULE-1, REQ-4 covers
    # nothing either (no RELATIONS at all).
    assert set(_gap_uids(all_scope, 1)) == {"REQ-2", "REQ-4"}

    # Gap 3: REQ-3 and REQ-4 have no verifying TEST_CASE; REQ-1 (TC-1) and
    # REQ-2 (TC-2) do.
    assert set(_gap_uids(all_scope, 2)) == {"REQ-3", "REQ-4"}

    # Gap 4: TC-2 is Not Executed; TC-1 is Passed and must not appear.
    assert _gap_uids(all_scope, 3) == ["TC-2"]
    assert all_scope.gaps[3].items[0].status == "Not Executed"


def test_gap_items_carry_a_clickable_link_and_title():
    traceability_index = _build_traceability_index()
    link_renderer = LinkRenderer(root_path="", static_path="_assets")

    scopes = EurobotTestDashboardGenerator.compute_scopes(
        traceability_index, link_renderer
    )
    all_scope = _scopes_by_key(scopes)["all"]

    gap1_item = all_scope.gaps[0].items[0]
    assert gap1_item.uid == "RULE-2"
    assert gap1_item.title == "Rule two"
    assert gap1_item.url != ""


def test_revision_only_scope_excludes_other_revisions():
    traceability_index = _build_traceability_index()
    link_renderer = LinkRenderer(root_path="", static_path="_assets")

    scopes = EurobotTestDashboardGenerator.compute_scopes(
        traceability_index, link_renderer
    )
    scopes_by_key = _scopes_by_key(scopes)

    # C1 only: REQ-1 and REQ-3 are in scope, REQ-2 (C2) and REQ-4 (TBD) are
    # not, so gap 2/3 only ever see REQ-3 (REQ-1 is fully covered/verified).
    c1_scope = scopes_by_key["C1"]
    assert _gap_uids(c1_scope, 1) == []
    assert _gap_uids(c1_scope, 2) == ["REQ-3"]

    # RULE-1's only covering requirements (REQ-1, REQ-3) are both C1, so it
    # stays covered at the C1 scope; RULE-2 is still uncovered everywhere.
    assert _gap_uids(c1_scope, 0) == ["RULE-2"]

    # TC-2 verifies REQ-2, which targets C2, so it is out of scope at C1.
    assert _gap_uids(c1_scope, 3) == []

    # C2 only: REQ-2 is in scope and still covers no rule; TC-2 (verifying
    # REQ-2) is back in scope and still Not Executed.
    c2_scope = scopes_by_key["C2"]
    assert _gap_uids(c2_scope, 1) == ["REQ-2"]
    assert _gap_uids(c2_scope, 3) == ["TC-2"]


def test_cumulative_scope_includes_earlier_revisions():
    traceability_index = _build_traceability_index()
    link_renderer = LinkRenderer(root_path="", static_path="_assets")

    scopes = EurobotTestDashboardGenerator.compute_scopes(
        traceability_index, link_renderer
    )
    scopes_by_key = _scopes_by_key(scopes)

    # "Up to and including C2" carries C1's own gap 3 item (REQ-3, which has
    # no verifying TEST_CASE) forward, unlike "C2 only"
    # (test_revision_only_scope_excludes_other_revisions asserts that scope
    # is empty for gap 3, since REQ-2 does have a verifying TEST_CASE).
    cumulative_c2 = scopes_by_key["C2_cumulative"]
    assert set(_gap_uids(cumulative_c2, 2)) == {"REQ-3"}


def test_revision_choice_order_matches_grammar_declaration():
    traceability_index = _build_traceability_index()
    link_renderer = LinkRenderer(root_path="", static_path="_assets")

    scopes = EurobotTestDashboardGenerator.compute_scopes(
        traceability_index, link_renderer
    )
    scope_keys = [scope_.key for scope_ in scopes]

    # "C1" (and its cumulative variant) must be resolved before "C2", per
    # TARGET_REVISION's declared SingleChoice(C1, C2) order, not by string
    # comparison.
    assert scope_keys == [
        "all",
        "C1",
        "C1_cumulative",
        "C2",
        "C2_cumulative",
    ]
