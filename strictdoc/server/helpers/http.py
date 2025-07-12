import hashlib
import os
import stat

from starlette.requests import Request


def get_etag(file_path: str) -> str:
    """
    Get an HTTP ETag value for a given file path.

    This implementation is taken from StackOverflow. The implementation itself
    is taken from Starlette.
    https://stackoverflow.com/a/76263874/598057

    NOTE: The Starlette's version is async and uses anyio.
    """

    assert os.path.isfile(file_path)
    stat_result = os.stat(file_path)
    mode = stat_result.st_mode
    if not stat.S_ISREG(mode):
        raise RuntimeError(f"File at path {file_path} is not a file.")

    # Calculate the etag based on file size and last modification time.
    etag_base = str(stat_result.st_mtime) + "-" + str(stat_result.st_size)
    etag = hashlib.md5(etag_base.encode()).hexdigest()
    return etag


def request_is_for_non_modified_file(
    request: Request, static_file: str
) -> bool:
    if "if-none-match" not in request.headers:
        return False

    # This request header comes up with quotes. Strip them.
    header_etag: str = request.headers["if-none-match"].strip('"')

    # We have copied the Etag calculation procedure from
    # Starlette's server code. One day this copy may diverge if
    # Starlette decides to implement something else.
    # In that case, the risk is that the 200/304 caching will stop
    # working but such a risk seems acceptable. There is an e2e test
    # that verifies that this branch is reached.
    file_etag = get_etag(static_file)
    return header_etag == file_etag
