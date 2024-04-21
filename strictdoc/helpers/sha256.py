# mypy: disable-error-code="no-untyped-def"
import hashlib


def get_sha256(byte_array):
    readable_hash = hashlib.sha256(byte_array).hexdigest()
    return readable_hash
