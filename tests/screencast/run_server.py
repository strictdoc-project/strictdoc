#!/usr/bin/env python3

from __future__ import annotations

import sys

from strictdoc_server import (
    SERVER_URL,
    start_server,
    stop_server,
    wait_for_server,
)


def main() -> int:
    try:
        server = start_server()
        wait_for_server(SERVER_URL, server)

        print(f"🚀 StrictDoc demo server: {SERVER_URL}")
        print("   Press Ctrl+C to stop.")

        server.wait()

    except KeyboardInterrupt:
        print("\n🛑 Stopping StrictDoc demo server.")

    except RuntimeError as error:
        print(error, file=sys.stderr)
        return 1

    finally:
        if "server" in locals():
            stop_server(server)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
