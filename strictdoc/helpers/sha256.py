import hashlib
import uuid


def get_sha256(byte_array: bytes) -> str:
    readable_hash = hashlib.sha256(byte_array).hexdigest()
    return readable_hash


def get_random_sha256() -> str:
    uid = uuid.uuid4()
    random_hash = hashlib.sha256(uid.bytes).hexdigest()
    return random_hash
