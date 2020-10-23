from functools import wraps
from time import time


def timing(name):
    def timing_internal(f):
        @wraps(f)
        def wrap(*args, **kw):
            ts = time()
            result = f(*args, **kw)
            te = time()
            print("Step '{}' took: {} sec".format(name, round(te-ts, 2)))
            return result
        return wrap
    return timing_internal
