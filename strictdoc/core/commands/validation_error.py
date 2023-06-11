from typing import Dict, List


class SingleValidationError(Exception):
    def __init__(self, message: str):
        super().__init__(message)


class MultipleValidationError(Exception):
    def __init__(self, message: str, errors: Dict[str, List[str]]):
        super().__init__(message)
        self.errors: Dict[str, List[str]] = errors
