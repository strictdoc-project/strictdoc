from dataclasses import dataclass, field
from typing import Dict, Union


@dataclass
class SourceFileStats:
    lines_total: int = 0
    lines_non_empty: int = 0
    lines_empty: int = 0
    lines_info: Dict[int, bool] = field(default_factory=dict)

    @classmethod
    def create(
        cls,
        string_or_bytes: Union[str, bytes],
    ) -> "SourceFileStats":
        if isinstance(string_or_bytes, bytes):
            string = string_or_bytes.decode("utf-8")
        else:
            string = string_or_bytes

        lines_non_empty = 0
        lines_empty = 0
        lines = string.splitlines()

        lines_info = {}
        for i_, line_ in enumerate(lines):
            line_is_not_empty = len(line_.strip()) > 0
            lines_info[i_ + 1] = line_is_not_empty
            if line_is_not_empty:
                lines_non_empty += 1
            else:
                lines_empty += 1

        return SourceFileStats(
            len(lines), lines_non_empty, lines_empty, lines_info
        )
