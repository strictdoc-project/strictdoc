from typing import Optional


class SectionChange:
    def __init__(
        self,
        *,
        matched_uid: Optional[str],
        free_text_modified: bool,
        colored_free_text_diff: Optional[str],
    ):
        if matched_uid is not None:
            assert len(matched_uid) > 0
        self.matched_uid: Optional[str] = matched_uid
        self.free_text_modified: bool = free_text_modified
        self.colored_free_text_diff: Optional[str] = colored_free_text_diff
