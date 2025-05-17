*** Test Cases ***

Foo Feature B
    [Documentation]    Test following requirements
    ...                @relation(REQ-B, scope=function)
    Log To Console    Let it pass

Bar Feature B
    [Documentation]    Test following requirements
    ...                @relation(REQ-B, scope=function)
    Fail    Let it fail
