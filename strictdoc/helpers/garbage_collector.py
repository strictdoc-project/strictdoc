"""
Tune Python's cyclic garbage collector for objects that live until the
process exits.
"""

import gc
from contextlib import contextmanager
from typing import Iterator, Tuple

# The garbage collector thresholds while long-lived objects are created, as
# gc.set_threshold(threshold0, threshold1, threshold2) takes them. The
# generational collector of CPython 3.10 and 3.12 uses the thresholds as
# follows. The defaults are (700, 10, 10).
#
# - threshold0 = 50_000: the collector runs a generation 0 collection after
#   50,000 more allocations than deallocations of tracked objects, instead
#   of after 700.
# - threshold1 = 20: every 20th collection also collects generation 1,
#   instead of every 10th. With threshold0, this is about every 1,000,000
#   allocations.
# - threshold2 = 10: every 10th generation 1 collection is a full
#   collection, as before. With threshold0 and threshold1, this is at most
#   every 10,000,000 allocations, instead of every 70,000. CPython also
#   skips a full collection until the objects that survived since the last
#   full collection reach 25 % of all old objects.
#
# A full collection traverses all tracked objects, also the long-lived
# ones, so rarer full collections save the most time. The young
# generations are still collected often enough to free short-lived
# garbage, for example the temporary objects of the SDoc parser. With the
# collector disabled instead, an export of the StrictDoc documentation
# without parallelization needed about twice the peak memory. The
# thresholds (20_000, 10, 10) and (100_000, 50, 100) gave the same export
# time as these.
LONG_LIVED_OBJECTS_GC_THRESHOLD: Tuple[int, int, int] = (50_000, 20, 10)


@contextmanager
def create_long_lived_objects() -> Iterator[None]:
    """
    Use case: static export.

    Create objects that live until the process exits, for example the
    traceability index of an export, with fewer garbage collections. After
    the block, freeze all objects, so that later garbage collections skip
    them.

    On an export without changes, the traceability index holds millions of
    objects that StrictDoc unpickles from the cache. Without this context
    manager, every full collection during the build of the traceability
    index, during the export, and at the exit of the process traverses
    these objects.

    Do not use this context manager in the server. The server builds a new
    traceability index after changes, and a frozen object is never freed.
    gc.freeze() also freezes the garbage that the collector has not freed
    yet. The amount of such garbage is limited by the thresholds above.
    """
    with run_fewer_garbage_collections():
        yield
    gc.freeze()


@contextmanager
def run_fewer_garbage_collections() -> Iterator[None]:
    """
    Use case: static export and server.

    Run the block with the thresholds above, and restore the previous
    thresholds after the block. Use this context manager for a block that
    creates many objects that live longer than the block, for example the
    search index data that the export of the static search index unpickles
    from the document cache. Without this context manager, these objects
    trigger full collections that traverse them again and again.
    """
    previous_threshold = gc.get_threshold()
    gc.set_threshold(*LONG_LIVED_OBJECTS_GC_THRESHOLD)
    try:
        yield
    finally:
        gc.set_threshold(*previous_threshold)
