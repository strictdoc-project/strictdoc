"""
Placement of document metadata in a Markdown document.

A Markdown document stores its document metadata in the YAML front
matter, in the metadata block after the H1 heading, or in both. The
reader records the placement in a MarkdownMetadataLayout. The writer uses
the layout to write each metadata field back to the same place:

- Without front matter, all fields go to the H1 metadata block.
- With front matter and without an H1 metadata block, all fields go to
  the front matter.
- With both, the reserved fields go to the H1 metadata block. A custom
  field goes back to the place it was read from. A new custom field goes
  to the front matter.

In each place, the reserved fields come first, in the order of
RESERVED_METADATA_KEYS. The custom fields follow in their own order.
"""

from dataclasses import dataclass
from typing import List, Optional, Sequence, Set, Tuple

# The document metadata keys that StrictDoc maps to its own document
# options. The keys are case-sensitive. The writer writes the reserved
# fields in this order.
RESERVED_METADATA_KEYS: Tuple[str, ...] = (
    "Grammar",
    "UID",
    "Version",
    "Date",
    "Classification",
    "Prefix",
)


@dataclass
class MarkdownMetadataLayout:
    has_front_matter: bool
    has_h1_metadata_block: bool
    # The keys of the custom fields that the reader read from the H1
    # metadata block.
    h1_metadata_block_keys: Set[str]


def place_metadata_entries(
    layout: Optional[MarkdownMetadataLayout],
    reserved_entries: Sequence[Tuple[str, str]],
    custom_entries: Sequence[Tuple[str, str]],
) -> Tuple[List[Tuple[str, str]], List[Tuple[str, str]]]:
    """
    Split metadata entries into front matter and H1 metadata block entries.

    Return a tuple (front_matter_entries, h1_metadata_block_entries).
    """
    if layout is None or not layout.has_front_matter:
        return [], [*reserved_entries, *custom_entries]

    if not layout.has_h1_metadata_block:
        return [*reserved_entries, *custom_entries], []

    front_matter_entries: List[Tuple[str, str]] = []
    h1_metadata_block_entries: List[Tuple[str, str]] = list(reserved_entries)
    for key_, value_ in custom_entries:
        if key_ in layout.h1_metadata_block_keys:
            h1_metadata_block_entries.append((key_, value_))
        else:
            front_matter_entries.append((key_, value_))
    return front_matter_entries, h1_metadata_block_entries
