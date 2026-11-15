"""
@relation(SDOC-SRS-51, scope=file)
"""
import re

from pypdf import PdfReader

reader = PdfReader("Output/html2pdf/pdf/input.pdf")

assert len(reader.pages) == 3, reader.pages

page1_text_normalized = re.sub(r"\d{4}-\d{2}-\d{2}", "XXXX-XX-XX",
    reader.pages[0].extract_text()
)

assert (
        page1_text_normalized
        == """\
Dummy Software Requirements
Speciﬁcation #1
Untitled Project Dummy Software Requirements Speciﬁcation #1
XXXX-XX-XX 1 / 3\
"""
), page1_text_normalized


page2_text_normalized = re.sub(r"\d{4}-\d{2}-\d{2}", "XXXX-XX-XX",
    reader.pages[1].extract_text()
)
assert (
        page2_text_normalized
        == """\
Table of contents
1 3
2 3
3 3
Dummy high-level requirement #1
Dummy high-level requirement #2
Dummy high-level requirement #3
Untitled Project Dummy Software Requirements Speciﬁcation #1
XXXX-XX-XX 2 / 3\
"""
), page2_text_normalized


page3_text_normalized = re.sub(r"\d{4}-\d{2}-\d{2}", "XXXX-XX-XX",
    reader.pages[2].extract_text()
)
assert (
        page3_text_normalized
        == """\
REQUIREMENT
1. Dummy high-level requirement #1
MID:
c165cc52af20417e9199e30a4e17f138
UID:
REQ-1
STATEMENT:
System ABC shall do 1.
REQUIREMENT
2. Dummy high-level requirement #2
MID:
74dddc4c55ac44ae83dc0f73ef8ed2aa
UID:
REQ-2
STATEMENT:
System ABC shall do 2.
REQUIREMENT
3. Dummy high-level requirement #3
MID:
fcbce0c486ac4d3189a7aa1dd646399e
UID:
REQ-3
STATEMENT:
System ABC shall do 3.
Untitled Project Dummy Software Requirements Speciﬁcation #1
XXXX-XX-XX 3 / 3\
"""
), page3_text_normalized
