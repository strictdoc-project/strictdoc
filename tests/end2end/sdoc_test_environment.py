WAIT_TIMEOUT = 5
POLL_TIMEOUT = 0.1
WARMUP_INTERVAL = 0
DOWNLOAD_FILE_TIMEOUT = 2
SERVER_TERM_TIMEOUT = 1


class SDocTestEnvironment:
    def __init__(
        self,
        *,
        is_parallel_execution: bool,
        wait_timeout_seconds: int,
        poll_timeout_seconds: float,
        warm_up_interval_seconds: int,
        download_file_timeout_seconds: int,
        server_term_timeout_seconds: int,
    ):
        self.is_parallel_execution = is_parallel_execution
        self.wait_timeout_seconds: int = wait_timeout_seconds
        self.poll_timeout_seconds: float = poll_timeout_seconds
        self.warm_up_interval_seconds: int = warm_up_interval_seconds

        # When Selenium clicks on a link that downloads a file, it takes some
        # time until the file actually appears on the file system.
        self.download_file_timeout_seconds: int = download_file_timeout_seconds

        self.server_term_timeout: int = server_term_timeout_seconds

    @staticmethod
    def create_default():
        return SDocTestEnvironment(
            is_parallel_execution=False,
            wait_timeout_seconds=WAIT_TIMEOUT,
            poll_timeout_seconds=POLL_TIMEOUT,
            warm_up_interval_seconds=WARMUP_INTERVAL,
            download_file_timeout_seconds=DOWNLOAD_FILE_TIMEOUT,
            server_term_timeout_seconds=SERVER_TERM_TIMEOUT,
        )

    def switch_to_long_timeouts(self):
        """
        Running Selenium tests on GitHub Actions CI is considerably slower.
        Passing the flag via env because pytest makes it hard to introduce an
        extra command-line argument when it is not used as a test fixture.
        """
        self.wait_timeout_seconds = 30
        # FIXME: This line is likely obsolete.
        self.poll_timeout_seconds = 1
        # FIXME: This line is likely obsolete.
        self.warm_up_interval_seconds = 0
        self.download_file_timeout_seconds = 5
        self.server_term_timeout = 5
