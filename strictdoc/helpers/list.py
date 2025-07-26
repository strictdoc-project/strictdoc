from collections import Counter
from typing import Any, List


def find_duplicates(lst: List[Any]) -> List[Any]:
    counter = Counter(lst)
    return [item for item, count in counter.items() if count > 1]
