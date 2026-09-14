from selenium.webdriver.support.wait import WebDriverWait

from tests.end2end.e2e_case import E2ECase


class BlockedTableFetch:
    def __init__(
        self,
        test_case: E2ECase,
        url_part: str,
        body_part: str,
    ) -> None:
        self.test_case = test_case
        self.test_case.execute_script(
            """
            const urlPart = arguments[0];
            const bodyPart = arguments[1];
            const originalFetch = window.fetch;
            const state = { release: null, handled: false };

            window.__tableEditBlockedFetch = state;
            window.__tableEditOriginalFetch = originalFetch;
            window.fetch = function(input, init) {
                // Inline forms send URLSearchParams. Autocomplete cells send
                // FormData. Serialize both so one helper can select a request
                // by the value that the browser will send to the server.
                const requestBody = init?.body;
                const body = requestBody instanceof FormData
                    ? new URLSearchParams(requestBody).toString()
                    : requestBody?.toString() || '';
                if (
                    state.release === null
                    && String(input).includes(urlPart)
                    && body.includes(bodyPart)
                ) {
                    return new Promise((resolve, reject) => {
                        state.reject = function() {
                            state.handled = true;
                            reject(new TypeError('Network error'));
                        };
                        state.release = async function() {
                            const response = await originalFetch(input, init);
                            const originalText = response.text.bind(response);
                            response.text = async function() {
                                const html = await originalText();
                                setTimeout(() => { state.handled = true; }, 0);
                                return html;
                            };
                            resolve(response);
                        };
                    });
                }
                return originalFetch(input, init);
            };
            """,
            url_part,
            body_part,
        )

    def wait_until_requested(self) -> None:
        WebDriverWait(self.test_case.driver, 10).until(
            lambda _: self.test_case.execute_script(
                "return window.__tableEditBlockedFetch.release !== null;"
            )
        )

    def release(self) -> None:
        self.test_case.execute_script(
            "window.__tableEditBlockedFetch.release();"
        )
        WebDriverWait(self.test_case.driver, 10).until(
            lambda _: self.test_case.execute_script(
                "return window.__tableEditBlockedFetch.handled;"
            )
        )

    def reject(self) -> None:
        self.test_case.execute_script(
            "window.__tableEditBlockedFetch.reject();"
        )
        WebDriverWait(self.test_case.driver, 10).until(
            lambda _: self.test_case.execute_script(
                "return window.__tableEditBlockedFetch.handled;"
            )
        )

    def restore(self) -> None:
        self.test_case.execute_script(
            "window.fetch = window.__tableEditOriginalFetch;"
            "delete window.__tableEditOriginalFetch;"
            "delete window.__tableEditBlockedFetch;"
        )
