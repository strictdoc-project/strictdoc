from strictdoc.helpers.net import is_valid_host


def test_is_valid_host():
    assert is_valid_host("192.168.1.1") == True  # Valid IPv4
    assert is_valid_host("::1") == True  # Valid IPv6
    assert is_valid_host("example.com") == True  # Valid hostname
    assert is_valid_host("sub.domain.org") == True  # Valid hostname
    assert is_valid_host("-badhost.com") == False  # Starts with `-`
    assert (
        is_valid_host("invalid_host!") == False
    )  # Contains invalid characters
    assert is_valid_host("a" * 300 + ".com") == False  # Too long (>253 chars)
