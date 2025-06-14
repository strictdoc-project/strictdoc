from typing import Dict, List


class ErrorObject:
    def __init__(self) -> None:
        self.errors: Dict[str, List[str]] = {}

    def any_errors(self) -> bool:
        return len(self.errors) > 0

    def get_errors(self, field_name: str) -> List[str]:
        if field_name not in self.errors:
            return []
        return self.errors[field_name]

    def add_error(self, field_name: str, error: str) -> None:
        error_container = self.errors.setdefault(field_name, [])
        error_container.append(error)
