from typing import Dict, List


class SingleValidationError(Exception):
    def __init__(self, message: str):
        super().__init__(message)


class MultipleValidationErrorAsList(Exception):
    def __init__(self, message: str, errors: List[str]):
        super().__init__(message)
        self.errors: List[str] = errors


class MultipleValidationError(Exception):
    def __init__(self, message: str, errors: Dict[str, List[str]]):
        super().__init__(message)
        self.errors: Dict[str, List[str]] = errors
