from typing import Callable, Iterable, List, Optional, Tuple, TypeVar

T = TypeVar("T")


def find_autocomplete_matches(
    query: str,
    candidates: Iterable[T],
    get_uid_and_title: Callable[[T], Tuple[str, str]],
    exact_match: Optional[T],
    limit: int,
) -> List[T]:
    """
    Returns the candidates whose UID and title together contain every word
    of the query, at most `limit` candidates.

    `exact_match` is the candidate whose UID equals the query, or None. It
    comes first, because the limit could cut it off. The caller finds it
    with the traceability index, so that the candidates are not read to the
    end.
    """

    matches: List[T] = [exact_match] if exact_match is not None else []
    query_words = query.lower().split()
    for candidate_ in candidates:
        if len(matches) >= limit:
            break
        if candidate_ is exact_match:
            continue
        uid_, title_ = get_uid_and_title(candidate_)
        words_ = (uid_ + " " + title_).lower()
        if all(word_ in words_ for word_ in query_words):
            matches.append(candidate_)
    return matches
