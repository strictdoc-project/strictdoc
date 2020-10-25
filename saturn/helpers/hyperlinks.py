import re


def string_to_anchor_id(string):
    return re.sub(r'[^A-Za-z0-9]+', '-', string)
