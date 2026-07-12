"""
@relation(SDOC-SRS-157, scope=file)
"""


def get_color(ratio: float) -> str:
    """
    Returns a hex color string representing the coverage level.
    - 0% coverage → light red (#ffaaaa)
    - 50% coverage → yellow (#ffffaa)
    - 100% coverage → light green (#aaffaa)
    """

    assert isinstance(ratio, float) and 0 <= ratio <= 1

    lightness = 0xAA

    red = (0xFF, lightness, lightness)
    yellow = (0xFF, 0xFF, lightness)
    green = (lightness, 0xFF, lightness)

    if ratio < 0.5:
        # Interpolate between red and yellow.
        t = ratio / 0.5
        r = int(red[0] + (yellow[0] - red[0]) * t)
        g = int(red[1] + (yellow[1] - red[1]) * t)
        b = int(red[2] + (yellow[2] - red[2]) * t)
    else:
        # Interpolate between yellow and green.
        t = (ratio - 0.5) / 0.5
        r = int(yellow[0] + (green[0] - yellow[0]) * t)
        g = int(yellow[1] + (green[1] - yellow[1]) * t)
        b = int(yellow[2] + (green[2] - yellow[2]) * t)

    return f"#{r:02x}{g:02x}{b:02x}"
