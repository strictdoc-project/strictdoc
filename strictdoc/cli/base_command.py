import argparse
from abc import ABC, abstractmethod

from strictdoc.helpers.parallelizer import Parallelizer


class CLIValidationError(Exception):
    pass


class BaseCommand(ABC):
    """Abstract base class for all StrictDoc CLI commands."""

    @classmethod
    @abstractmethod
    def add_arguments(cls, parser: argparse.ArgumentParser) -> None:
        """Add command-specific arguments to the parser."""
        pass

    @abstractmethod
    def run(self, parallelizer: Parallelizer) -> None:
        """Execute the command."""
        pass
