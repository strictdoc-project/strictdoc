import os
import sys

from seleniumbase.config import settings

from tests.end2end.sdoc_test_environment import SDocTestEnvironment

STRICTDOC_PATH = os.path.abspath(os.path.join(__file__, "../../.."))
assert os.path.exists(STRICTDOC_PATH), f"does not exist: {STRICTDOC_PATH}"
sys.path.append(STRICTDOC_PATH)

DOWNLOADED_FILES_PATH = os.path.join(STRICTDOC_PATH, "downloaded_files")


if os.getenv("STRICTDOC_LONGER_TIMEOUTS") is not None:
    WAIT_TIMEOUT = 30
    POLL_TIMEOUT = 2000
    WARMUP_INTERVAL = 3
    DOWNLOAD_FILE_TIMEOUT = 5
    # Selenium timeout settings
    settings.MINI_TIMEOUT = 5
    settings.SMALL_TIMEOUT = 10
    settings.LARGE_TIMEOUT = 15
    settings.EXTREME_TIMEOUT = 30
else:
    WAIT_TIMEOUT = 5  # Seconds
    POLL_TIMEOUT = 1000  # Milliseconds
    WARMUP_INTERVAL = 0
    DOWNLOAD_FILE_TIMEOUT = 2
    # Selenium timeout settings
    settings.MINI_TIMEOUT = 2
    settings.SMALL_TIMEOUT = 7
    settings.LARGE_TIMEOUT = 10
    settings.EXTREME_TIMEOUT = 30

test_environment = SDocTestEnvironment(
    is_parallel_execution="STRICTDOC_PARALLELIZE" in os.environ,
    wait_timeout_seconds=WAIT_TIMEOUT,
    poll_timeout_milliseconds=POLL_TIMEOUT,
    warm_up_interval_seconds=WARMUP_INTERVAL,
    download_file_timeout_seconds=DOWNLOAD_FILE_TIMEOUT,
)
