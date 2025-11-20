import hashlib
import uuid
from typing import Union


def get_sha256(byte_array: bytes) -> str:
    readable_hash = hashlib.sha256(byte_array).hexdigest()
    return readable_hash


def get_random_sha256() -> str:
    uid = uuid.uuid4()
    random_hash = hashlib.sha256(uid.bytes).hexdigest()
    return random_hash


def is_sha256(content: Union[bytes, str]) -> bool:
    return len(content) == 64
