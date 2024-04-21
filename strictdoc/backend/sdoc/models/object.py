# mypy: disable-error-code="no-untyped-def"
from abc import ABC, abstractmethod


class SDocObject(ABC):
    @property
    @abstractmethod
    def is_requirement(self):
        raise NotImplementedError(self)

    @property
    @abstractmethod
    def is_section(self):
        raise NotImplementedError(self)

    @property
    @abstractmethod
    def is_composite_requirement(self):
        raise NotImplementedError(self)
