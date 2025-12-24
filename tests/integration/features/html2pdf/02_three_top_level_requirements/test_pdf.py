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
XXXX-XX-XX 1/3\
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
XXXX-XX-XX 2/3\
"""
), page2_text_normalized


page3_text_normalized = re.sub(r"\d{4}-\d{2}-\d{2}", "XXXX-XX-XX",
    reader.pages[2].extract_text()
    .replace("R E Q-", "R E Q -")
)
assert (
        page3_text_normalized
        == """\
REQUIREMENT
1. Dummy high-level requirement #1
M I D :
c 1 6 5 c c 5 2 a f2 0 4 1 7 e 9 1 9 9 e 3 0 a 4 e 1 7 f1 3 8
U I D :
R E Q - 1
S T A T E M E N T :
System ABC shall do 1.
REQUIREMENT
2. Dummy high-level requirement #2
M I D :
7 4 d d d c 4 c 5 5 a c 4 4 a e 8 3 d c 0 f7 3 e f8 e d 2 a a
U I D :
R E Q - 2
S T A T E M E N T :
System ABC shall do 2.
REQUIREMENT
3. Dummy high-level requirement #3
M I D :
fc b c e 0 c 4 8 6 a c 4 d 3 1 8 9 a 7 a a 1 d d 6 4 6 3 9 9 e
U I D :
R E Q - 3
S T A T E M E N T :
System ABC shall do 3.
Untitled Project Dummy Software Requirements Speciﬁcation #1
XXXX-XX-XX 3/3\
"""
), page3_text_normalized
