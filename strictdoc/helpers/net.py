import ipaddress
import re
from urllib.parse import urlparse

# Regex for a valid hostname (RFC 1034/1035)
HOSTNAME_REGEX = re.compile(
    r"^(?!-)[A-Za-z0-9-]{1,63}(?<!-)(\.[A-Za-z0-9-]{1,63})*$"
)


def is_valid_host(host: str) -> bool:
    """
    Validate that a string is either an IP address or a hostname.
    """
    try:
        # Check if it's a valid IP address (IPv4 or IPv6).
        ipaddress.ip_address(host)
        return True
    except ValueError:
        # If not an IP, check if it's a valid hostname.
        return bool(HOSTNAME_REGEX.fullmatch(host)) and len(host) <= 253


def is_valid_url(url: str) -> bool:
    """
    Validate that a string is a well-formed absolute http(s) URL.
    """
    try:
        parsed = urlparse(url)
    except ValueError:
        return False
    return parsed.scheme in ("http", "https") and bool(parsed.netloc)
