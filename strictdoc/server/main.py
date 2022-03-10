import argparse
import os
import sys

import uvicorn

try:
    strictdoc_path = os.path.abspath(os.path.join(__file__, "../../.."))
    assert os.path.exists(strictdoc_path), f"does not exist: {strictdoc_path}"
    sys.path.append(strictdoc_path)

    from strictdoc.server.app import ENV_INPUT_PATH
except AssertionError:
    print("Cannot find strictdoc's root folder.")
    sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input_path")

    parser.add_argument("--reload", default=True, action="store_true")
    parser.add_argument("--no-reload", dest="reload", action="store_false")
    args = parser.parse_args()

    input_path = args.input_path
    assert os.path.exists(input_path)

    os.environ[ENV_INPUT_PATH] = input_path

    uvicorn.run(
        "strictdoc.server.app:strictdoc_production_app",
        app_dir=".",
        host="127.0.0.1",
        port=8001,
        log_level="info",
        reload=args.reload,
        factory=True,
    )
else:
    assert (
        ENV_INPUT_PATH in os.environ
    ), "ENV_INPUT_PATH should point to a folder with *.sdoc content."
