# mypy: disable-error-code="no-untyped-call,no-untyped-def"
# Custom argparse type representing a bounded int
# https://stackoverflow.com/a/61411431/598057
import argparse


class IntRange:
    def __init__(self, imin=None, imax=None):
        self.imin = imin
        self.imax = imax

    def __call__(self, arg):
        try:
            value = int(arg)
        except ValueError as exc:
            raise self.exception() from exc
        if (self.imin is not None and value < self.imin) or (
            self.imax is not None and value > self.imax
        ):
            raise self.exception()
        return value

    def exception(self):
        if self.imin is not None and self.imax is not None:
            return argparse.ArgumentTypeError(
                f"Must be an integer in the range [{self.imin}, {self.imax}]"
            )
        if self.imin is not None:
            return argparse.ArgumentTypeError(
                f"Must be an integer >= {self.imin}"
            )
        if self.imax is not None:
            return argparse.ArgumentTypeError(
                f"Must be an integer <= {self.imax}"
            )
        return argparse.ArgumentTypeError("Must be an integer")
