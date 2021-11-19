import re

REGEX_SUBREQ = re.compile("(\\.)([a-z])$")


def match_letter_uid(uid):
    match = REGEX_SUBREQ.search(uid)
    if match:
        return match.group(2)
    return None
