import atexit
import sys
from dataclasses import dataclass, field
from typing import Dict


@dataclass
class DeprecationEngine:
    deprecations: Dict[str, str] = field(default_factory=dict)

    def add_message(
        self, deprecation_key: str, deprecation_message: str
    ) -> None:
        if deprecation_key in self.deprecations:
            return

        self._print(deprecation_message)

        self.deprecations[deprecation_key] = deprecation_message

    def print_all_messages(self) -> None:  # pragma: no cover
        """
        Print all deprecation messages collected so far.

        It is assumed that this function is at least called during the program
        termination, so that a user can see the deprecation messages. During
        the termination, the code coverage is normally already stopped, so the
        function is excluded from code coverage.
        """

        if len(self.deprecations) == 0:
            return

        self._print("DEPRECATION: This project has the following issues:")
        for message_idx_, message_ in enumerate(
            self.deprecations.values(), start=1
        ):
            self._print(f"\nIssue #{message_idx_}\n")
            self._print(message_)
        sys.stdout.flush()

    @staticmethod
    def _print(message: str) -> None:
        print(f"\x1b[33m{message}\x1b[0m", flush=True)  # noqa: T201


DEPRECATION_ENGINE = DeprecationEngine()

atexit.register(DEPRECATION_ENGINE.print_all_messages)
