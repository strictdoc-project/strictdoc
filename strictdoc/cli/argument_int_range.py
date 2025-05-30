# Custom argparse type representing a bounded integer range.
#
# https://stackoverflow.com/a/61411431/598057
import argparse
from typing import Any, Optional, Union


class IntRange:
    def __init__(self, imin: int, imax: int) -> None:
        self.imin: int = imin
        self.imax: int = imax

    def __call__(self, arg: Any) -> Union[int, argparse.ArgumentTypeError]:
        value: Optional[int]
        try:
            value = int(arg)
        except ValueError:
            value = None

        if value is not None and self.imin <= value <= self.imax:
            return value

        raise argparse.ArgumentTypeError(
            f"Must be an integer in the range [{self.imin}, {self.imax}]"
        )
