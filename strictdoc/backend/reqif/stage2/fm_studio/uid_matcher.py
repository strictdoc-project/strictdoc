import re

REGEX_SUBREQ = re.compile("(\\.)([a-z])$")
REGEX_SUBREQ_BULLET = re.compile("(\\.)\\*\\[(\\d+)\\]$")
REGEX_SUBREQ_CONTINUATION = re.compile("(.*)\\[(\\d+)\\]$")


def match_letter_uid(uid):
    match = REGEX_SUBREQ.search(uid)
    if match:
        return match.group(2)
    return None


def match_bullet_uid(uid):
    match = REGEX_SUBREQ_BULLET.search(uid)
    if match:
        return match.group(2)
    return None


def match_continuation_uid(uid):
    match = REGEX_SUBREQ_CONTINUATION.search(uid)
    if match:
        return match.group(2)
    return None
