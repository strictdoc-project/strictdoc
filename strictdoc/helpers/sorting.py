# mypy: disable-error-code="no-untyped-call,no-untyped-def"
import re


def atoi(text):
    return int(text) if text.isdigit() else text


def alphanumeric_sort(text):
    """
    Sort keys in the human (alphanumeric) order.

    alist.sort(key=alphanumeric_sort) sorts in human order
    http://nedbatchelder.com/blog/200712/human_sorting.html
    (See Toothy's implementation in the comments)
    """

    return [atoi(c) for c in re.split(r"(\d+)", text)]
