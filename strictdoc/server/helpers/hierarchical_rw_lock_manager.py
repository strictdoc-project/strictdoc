import threading
from contextlib import contextmanager
from typing import Dict, Iterable, Iterator, Optional, Set, Tuple

from strictdoc.server.helpers.rw_lock import RWLock


class HierarchicalRWLockManager:
    """
    Coordinate coarse and fine-grained read/write locks.

    Lock hierarchy:
    1) global lock (coarse gate), then
    2) per-resource locks (fine-grained subset).

    The subset lock acquires the global lock in read mode first, then acquires
    resource locks in a canonical sorted order to prevent deadlocks.

    Important:
    - This lock manager is not re-entrant.
    - Do not call acquire_subset() from code that already holds the manager's
      global read/write lock.
    """

    def __init__(self) -> None:
        self._global_lock = RWLock()
        self._resource_locks: Dict[str, RWLock] = {}
        self._resource_locks_guard = threading.Lock()

    @contextmanager
    def acquire_global_read(self) -> Iterator[None]:
        with self._global_lock.read():
            yield

    @contextmanager
    def acquire_global_write(self) -> Iterator[None]:
        with self._global_lock.write():
            yield

    @contextmanager
    def acquire_subset(
        self,
        *,
        read_ids: Optional[Iterable[str]] = None,
        write_ids: Optional[Iterable[str]] = None,
    ) -> Iterator[None]:
        normalized_read_ids, normalized_write_ids = self._normalize_lock_sets(
            read_ids=read_ids, write_ids=write_ids
        )
        all_resource_ids = sorted(normalized_read_ids | normalized_write_ids)

        # Acquire global read lock first so coarse "global write" users are
        # mutually exclusive with all fine-grained subset operations.
        with self._global_lock.read():
            acquired_resource_locks: list[Tuple[RWLock, bool]] = []
            try:
                for resource_id in all_resource_ids:
                    resource_lock = self._get_or_create_resource_lock(
                        resource_id
                    )
                    if resource_id in normalized_write_ids:
                        resource_lock.acquire_write()
                        acquired_resource_locks.append((resource_lock, True))
                    else:
                        resource_lock.acquire_read()
                        acquired_resource_locks.append((resource_lock, False))
                yield
            finally:
                for resource_lock, is_write_mode in reversed(
                    acquired_resource_locks
                ):
                    if is_write_mode:
                        resource_lock.release_write()
                    else:
                        resource_lock.release_read()

    def _get_or_create_resource_lock(self, resource_id: str) -> RWLock:
        assert isinstance(resource_id, str), resource_id
        with self._resource_locks_guard:
            existing_lock = self._resource_locks.get(resource_id)
            if existing_lock is not None:
                return existing_lock
            new_lock = RWLock()
            self._resource_locks[resource_id] = new_lock
            return new_lock

    @staticmethod
    def _normalize_lock_sets(
        *,
        read_ids: Optional[Iterable[str]],
        write_ids: Optional[Iterable[str]],
    ) -> Tuple[Set[str], Set[str]]:
        normalized_read_ids: Set[str] = set(read_ids or ())
        normalized_write_ids: Set[str] = set(write_ids or ())

        # Write lock dominates read lock for the same resource.
        normalized_read_ids -= normalized_write_ids
        return normalized_read_ids, normalized_write_ids
