import contextlib
from functools import wraps
from time import time

from strictdoc.helpers.math import round_up


def timing_decorator(name):
    def timing_internal(f):
        @wraps(f)
        def wrap(*args, **kw):
            print(f"Step '{name}' start", flush=True)
            ts = time()
            result = f(*args, **kw)
            te = time()
            print(
                "Step '{}' took: {} sec".format(name, round_up(te - ts, 2)),
                flush=True,
            )
            return result

        return wrap

    return timing_internal


@contextlib.contextmanager
def measure_performance(title):
    ts = time()
    yield
    te = time()

    padded_name = "{title} ".format(title=title).ljust(60, ".")
    padded_time = " {:0.2f}".format((te - ts)).rjust(6, ".")
    print("{}{}s".format(padded_name, padded_time))
