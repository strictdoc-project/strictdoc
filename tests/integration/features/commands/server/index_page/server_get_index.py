"""
Start "strictdoc server" with the given command, request the index page,
and print its HTTP status.

Usage: python server_get_index.py <input path> <output path> <strictdoc...>
"""

import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request

TIMEOUT_SECONDS = 120


def find_free_port() -> int:
    # "strictdoc server" accepts ports in the range [1024, 65000].
    for port in range(18001, 19000):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            try:
                sock.bind(("127.0.0.1", port))
            except OSError:
                continue
            return port
    raise RuntimeError("no free port found")


def main() -> None:
    input_path, output_path, *strictdoc_command = sys.argv[1:]
    port = find_free_port()
    process = subprocess.Popen(
        [
            *strictdoc_command,
            "server",
            input_path,
            "--output-path",
            output_path,
            "--port",
            str(port),
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    status = None
    try:
        deadline = time.time() + TIMEOUT_SECONDS
        while time.time() < deadline and process.poll() is None:
            try:
                with urllib.request.urlopen(
                    f"http://127.0.0.1:{port}/", timeout=30
                ) as response:
                    status = response.status
                break
            except urllib.error.HTTPError as error:
                status = error.code
                break
            except OSError:
                time.sleep(0.5)
    finally:
        process.terminate()
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()
    print(f"HTTP status: {status}")  # noqa: T201


main()
