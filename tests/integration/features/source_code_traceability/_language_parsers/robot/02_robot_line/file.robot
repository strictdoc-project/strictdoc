*** Settings ***
Documentation     Example using the space separated format.

*** Variables ***
# @relation(REQ-1, scope=line)
${MESSAGE}        Hello, world!

*** Test Cases ***
My Test
    [Documentation]    Test following requirements
# @relation(REQ-1, scope=line)
    Log    ${MESSAGE}
    My Keyword    ${MESSAGE}
    My Other Keyword
