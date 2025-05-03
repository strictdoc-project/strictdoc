*** Settings ***
Documentation     Example using the space separated format.

*** Test Cases ***
My Test
    [Documentation]    Test following requirements
    ...                @relation(REQ-1, scope=function)
    My Other Keyword

My Other Test
    [Tags]    @relation(REQ-1, REQ-2, scope=function)
    My Other Keyword

Yet Another Test
    # @relation(REQ-2, scope=function)
    My Other Keyword
