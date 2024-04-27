# mypy: disable-error-code="no-untyped-def"
import hashlib


def get_md5(obj: str):
    return hashlib.md5(obj.encode("utf-8")).hexdigest()


def get_file_md5(path: str, buf_size: int = 65536) -> str:
    m = hashlib.md5()
    with open(path, "rb") as f:
        b = f.read(buf_size)
        while len(b) > 0:
            m.update(b)
            b = f.read(buf_size)
    return m.hexdigest()
