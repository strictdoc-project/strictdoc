from typing import List, Optional, Tuple

from strictdoc.server.helpers.autocomplete import find_autocomplete_matches

Candidate = Tuple[str, str]


def find(
    query: str,
    candidates: List[Candidate],
    exact_match: Optional[Candidate] = None,
    limit: int = 50,
) -> List[str]:
    matches = find_autocomplete_matches(
        query, candidates, lambda candidate_: candidate_, exact_match, limit
    )
    return [uid_ for uid_, _ in matches]


def test_every_query_word_in_uid_or_title():
    candidates = [("REQ-1", "Export to PDF"), ("REQ-2", "Export to HTML")]
    assert find("export pdf", candidates) == ["REQ-1"]
    assert find("REQ html", candidates) == ["REQ-2"]
    assert find("", candidates) == ["REQ-1", "REQ-2"]
    assert find("missing", candidates) == []


def test_limit():
    candidates = [(f"REQ-{index_}", "") for index_ in range(10)]
    assert len(find("REQ", candidates, limit=3)) == 3


def test_exact_match_comes_first_and_once():
    candidates = [(f"REQ-1{index_}", "") for index_ in range(10)]
    exact_match = ("REQ-1", "")
    candidates.append(exact_match)

    matches = find("REQ-1", candidates, exact_match=exact_match, limit=3)
    assert matches == ["REQ-1", "REQ-10", "REQ-11"]

    matches = find("REQ-1", candidates, exact_match=exact_match)
    assert matches[0] == "REQ-1"
    assert matches.count("REQ-1") == 1
