*** Test Cases ***
Check Valid Login
    [Documentation]    @relation(REQ-AUTH-001, scope=function)
    ...    UID: TC-AUTH-001
    ...    INTENTION: Verify that valid credentials grant access.
    ...    EXPECTED_RESULTS: User is redirected to dashboard.
    Precondition	System is commissioned

    Do		Login to Web UI as "test", password "test".
    Expect	Login is possible.

Login With Invalid Credentials
    [Documentation]    @relation(REQ-AUTH-002, scope=function)
    ...    UID: TC-AUTH-002
    ...    INTENTION: Verify that login fails with wrong password
    ...    EXPECTED_RESULTS: Error message is shown, new login dialog appears.
    Precondition	System is commissioned

    Do		Login to Web UI with user "none", password "none"
    Expect	Login is rejected.
