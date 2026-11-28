import gc
from typing import Iterator, List

import pytest

from strictdoc.helpers.garbage_collector import (
    LONG_LIVED_OBJECTS_GC_THRESHOLD,
    create_long_lived_objects,
    run_fewer_garbage_collections,
)


@pytest.fixture(autouse=True)
def restore_garbage_collector() -> Iterator[None]:
    """
    Keep the frozen objects and the thresholds of a test out of other tests.
    """
    threshold = gc.get_threshold()
    gc.unfreeze()
    yield
    gc.unfreeze()
    gc.set_threshold(*threshold)


def test_01_raises_thresholds_inside_the_block_only() -> None:
    threshold_before = gc.get_threshold()

    with create_long_lived_objects():
        assert gc.get_threshold() == LONG_LIVED_OBJECTS_GC_THRESHOLD

    assert gc.get_threshold() == threshold_before


def test_02_freezes_the_objects_created_inside_the_block() -> None:
    assert gc.get_freeze_count() == 0

    with create_long_lived_objects():
        long_lived_objects: List[List[int]] = [
            [index_] for index_ in range(1000)
        ]

    assert gc.get_freeze_count() >= len(long_lived_objects)
    # A full collection skips the frozen objects.
    gc.collect()
    assert gc.get_freeze_count() >= len(long_lived_objects)


def test_03_restores_thresholds_and_freezes_nothing_on_exception() -> None:
    threshold_before = gc.get_threshold()

    with pytest.raises(RuntimeError):
        with create_long_lived_objects():
            raise RuntimeError("Build failed.")

    assert gc.get_threshold() == threshold_before
    assert gc.get_freeze_count() == 0


def test_04_run_fewer_garbage_collections_does_not_freeze() -> None:
    threshold_before = gc.get_threshold()

    with run_fewer_garbage_collections():
        assert gc.get_threshold() == LONG_LIVED_OBJECTS_GC_THRESHOLD
        objects: List[List[int]] = [[index_] for index_ in range(1000)]

    assert gc.get_threshold() == threshold_before
    assert gc.get_freeze_count() == 0
    assert len(objects) == 1000
