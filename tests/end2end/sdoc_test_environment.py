class SDocTestEnvironment:
    def __init__(
        self,
        *,
        is_parallel_execution: bool,
        wait_timeout_seconds: int,
        poll_timeout_seconds: int,
        warm_up_interval_seconds: int,
        download_file_timeout_seconds: int,
        server_term_timeout_seconds: int,
    ):
        self.is_parallel_execution = is_parallel_execution
        self.wait_timeout_seconds: int = wait_timeout_seconds
        self.poll_timeout_seconds: int = poll_timeout_seconds
        self.warm_up_interval_seconds: int = warm_up_interval_seconds

        # When Selenium clicks on a link that downloads a file, it takes some
        # time until the file actually appears on the file system.
        self.download_file_timeout_seconds: int = download_file_timeout_seconds

        self.server_term_timeout: int = server_term_timeout_seconds
