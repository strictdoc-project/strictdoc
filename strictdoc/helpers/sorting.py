import re
from typing import List, Union


def atoi(text: str) -> Union[int, str]:
    return int(text) if text.isdigit() else text


def alphanumeric_sort(text: str) -> List[Union[int, str]]:
    """
    Sort keys in the human (alphanumeric) order.

    alist.sort(key=alphanumeric_sort) sorts in human order
    http://nedbatchelder.com/blog/200712/human_sorting.html
    (See Toothy's implementation in the comments)
    """

    return [atoi(c) for c in re.split(r"(\d+)", text)]
