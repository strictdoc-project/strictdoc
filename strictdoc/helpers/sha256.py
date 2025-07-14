import hashlib


def get_sha256(byte_array: bytes) -> str:
    readable_hash = hashlib.sha256(byte_array).hexdigest()
    return readable_hash
