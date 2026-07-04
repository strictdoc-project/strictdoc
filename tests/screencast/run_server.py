#!/usr/bin/env python3

from __future__ import annotations

import os
import sys

STRICTDOC_ROOT = os.path.abspath(os.path.join(__file__, "../../.."))
assert os.path.isdir(STRICTDOC_ROOT), STRICTDOC_ROOT
sys.path.insert(0, STRICTDOC_ROOT)

from tests.end2end.server import SDocTestServer  # noqa: E402
from tests.screencast.fixture import (  # noqa: E402
    DEV_SERVER_PORT,
    FIXTURE_CONFIG,
    FIXTURE_DIR,
)


def main() -> int:
    try:
        with SDocTestServer(
            input_path=str(FIXTURE_DIR),
            config_path=str(FIXTURE_CONFIG),
            port=DEV_SERVER_PORT,
        ) as server:
            print(f"🚀 StrictDoc demo server: {server.get_host_and_port()}")
            print("   Press Ctrl+C to stop.")

            server.process.wait()

    except KeyboardInterrupt:
        print("\n🛑 Stopping StrictDoc demo server.")

    except OSError as error:
        print(error, file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
