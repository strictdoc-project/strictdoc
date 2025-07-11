*** Settings ***
Documentation     Example using the space separated format.

*** Variables ***
# @relation(REQ-1, scope=range_start)
${MESSAGE}        Hello, world!
# @relation(REQ-1, scope=range_end)

*** Test Cases ***
My Test
    [Documentation]    Test following requirements
# @relation(REQ-1, scope=range_start)
    Log    ${MESSAGE}
    My Keyword    ${MESSAGE}
# @relation(REQ-1, scope=range_end)
    My Other Keyword
