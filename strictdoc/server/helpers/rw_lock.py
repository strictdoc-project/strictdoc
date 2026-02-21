import threading
from contextlib import contextmanager
from typing import Iterator


class RWLock:
    """
    A minimal readers-writer lock for single-process use.
    """

    def __init__(self) -> None:
        self._readers = 0
        self._writer = False
        self._condition = threading.Condition()

    def acquire_read(self) -> None:
        with self._condition:
            while self._writer:
                self._condition.wait()
            self._readers += 1

    def release_read(self) -> None:
        with self._condition:
            self._readers -= 1
            if self._readers == 0:
                self._condition.notify_all()

    def acquire_write(self) -> None:
        with self._condition:
            while self._writer or self._readers > 0:
                self._condition.wait()
            self._writer = True

    def release_write(self) -> None:
        with self._condition:
            self._writer = False
            self._condition.notify_all()

    @contextmanager
    def read(self) -> Iterator[None]:
        self.acquire_read()
        try:
            yield
        finally:
            self.release_read()

    @contextmanager
    def write(self) -> Iterator[None]:
        self.acquire_write()
        try:
            yield
        finally:
            self.release_write()
